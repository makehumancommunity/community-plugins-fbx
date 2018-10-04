# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Script copyright (C) Campbell Barton, Bastien Montagne


import math
import time

from collections import namedtuple, OrderedDict
from collections.abc import Iterable
from itertools import zip_longest, chain

from . import encode_bin, data_types


# "Constants"
FBX_VERSION = 7400
FBX_HEADER_VERSION = 1003
FBX_SCENEINFO_VERSION = 100
FBX_TEMPLATES_VERSION = 100

FBX_MODELS_VERSION = 232

FBX_GEOMETRY_VERSION = 124
# Revert back normals to 101 (simple 3D values) for now, 102 (4D + weights) seems not well supported by most apps
# currently, apart from some AD products.
FBX_GEOMETRY_NORMAL_VERSION = 101
FBX_GEOMETRY_BINORMAL_VERSION = 101
FBX_GEOMETRY_TANGENT_VERSION = 101
FBX_GEOMETRY_SMOOTHING_VERSION = 102
FBX_GEOMETRY_VCOLOR_VERSION = 101
FBX_GEOMETRY_UV_VERSION = 101
FBX_GEOMETRY_MATERIAL_VERSION = 101
FBX_GEOMETRY_LAYER_VERSION = 100
FBX_GEOMETRY_SHAPE_VERSION = 100
FBX_DEFORMER_SHAPE_VERSION = 100
FBX_DEFORMER_SHAPECHANNEL_VERSION = 100
FBX_POSE_BIND_VERSION = 100
FBX_DEFORMER_SKIN_VERSION = 101
FBX_DEFORMER_CLUSTER_VERSION = 100
FBX_MATERIAL_VERSION = 102
FBX_TEXTURE_VERSION = 202
FBX_ANIM_KEY_VERSION = 4008

FBX_NAME_CLASS_SEP = b"\x00\x01"
FBX_ANIM_PROPSGROUP_NAME = "d"

FBX_KTIME = 46186158000  # This is the number of "ktimes" in one second (yep, precision over the nanosecond...)


#MAT_CONVERT_LAMP = Matrix.Rotation(math.pi / 2.0, 4, 'X')  # Blender is -Z, FBX is -Y.
#MAT_CONVERT_CAMERA = Matrix.Rotation(math.pi / 2.0, 4, 'Y')  # Blender is -Z, FBX is +X.
# XXX I can't get this working :(
# MAT_CONVERT_BONE = Matrix.Rotation(math.pi / 2.0, 4, 'Z')  # Blender is +Y, FBX is -X.
#MAT_CONVERT_BONE = Matrix()


BLENDER_OTHER_OBJECT_TYPES = {'CURVE', 'SURFACE', 'FONT', 'META'}
BLENDER_OBJECT_TYPES_MESHLIKE = {'MESH'} | BLENDER_OTHER_OBJECT_TYPES


# Lamps.
FBX_LIGHT_TYPES = {
    'POINT': 0,  # Point.
    'SUN': 1,    # Directional.
    'SPOT': 2,   # Spot.
    'HEMI': 1,   # Directional.
    'AREA': 3,   # Area.
}
FBX_LIGHT_DECAY_TYPES = {
    'CONSTANT': 0,                   # None.
    'INVERSE_LINEAR': 1,             # Linear.
    'INVERSE_SQUARE': 2,             # Quadratic.
    'CUSTOM_CURVE': 2,               # Quadratic.
    'LINEAR_QUADRATIC_WEIGHTED': 2,  # Quadratic.
}


RIGHT_HAND_AXES = {
    # Up, Forward -> FBX values (tuples of (axis, sign), Up, Front, Coord).
    ( 'X', '-Y'): ((0,  1), (1,  1), (2,  1)),
    ( 'X',  'Y'): ((0,  1), (1, -1), (2, -1)),
    ( 'X', '-Z'): ((0,  1), (2,  1), (1, -1)),
    ( 'X',  'Z'): ((0,  1), (2, -1), (1,  1)),
    ('-X', '-Y'): ((0, -1), (1,  1), (2, -1)),
    ('-X',  'Y'): ((0, -1), (1, -1), (2,  1)),
    ('-X', '-Z'): ((0, -1), (2,  1), (1,  1)),
    ('-X',  'Z'): ((0, -1), (2, -1), (1, -1)),
    ( 'Y', '-X'): ((1,  1), (0,  1), (2, -1)),
    ( 'Y',  'X'): ((1,  1), (0, -1), (2,  1)),
    ( 'Y', '-Z'): ((1,  1), (2,  1), (0,  1)),
    ( 'Y',  'Z'): ((1,  1), (2, -1), (0, -1)),
    ('-Y', '-X'): ((1, -1), (0,  1), (2,  1)),
    ('-Y',  'X'): ((1, -1), (0, -1), (2, -1)),
    ('-Y', '-Z'): ((1, -1), (2,  1), (0, -1)),
    ('-Y',  'Z'): ((1, -1), (2, -1), (0,  1)),
    ( 'Z', '-X'): ((2,  1), (0,  1), (1,  1)),
    ( 'Z',  'X'): ((2,  1), (0, -1), (1, -1)),
    ( 'Z', '-Y'): ((2,  1), (1,  1), (0, -1)),
    ( 'Z',  'Y'): ((2,  1), (1, -1), (0,  1)),  # Blender system!
    ('-Z', '-X'): ((2, -1), (0,  1), (1, -1)),
    ('-Z',  'X'): ((2, -1), (0, -1), (1,  1)),
    ('-Z', '-Y'): ((2, -1), (1,  1), (0,  1)),
    ('-Z',  'Y'): ((2, -1), (1, -1), (0, -1)),
}


FBX_FRAMERATES = (
    (-1.0, 14),  # Custom framerate.
    (120.0, 1),
    (100.0, 2),
    (60.0, 3),
    (50.0, 4),
    (48.0, 5),
    (30.0, 6),  # BW NTSC.
    (30.0 / 1.001, 9),  # Color NTSC.
    (25.0, 10),
    (24.0, 11),
    (24.0 / 1.001, 13),
    (96.0, 15),
    (72.0, 16),
    (60.0 / 1.001, 17),
)


# ##### Misc utilities #####

DO_PERFMON = True

if DO_PERFMON:
    class PerfMon():
        def __init__(self):
            self.level = -1
            self.ref_time = []

        def level_up(self, message=""):
            self.level += 1
            self.ref_time.append(None)
            if message:
                print("\t" * self.level, message, sep="")

        def level_down(self, message=""):
            if not self.ref_time:
                if message:
                    print(message)
                return
            ref_time = self.ref_time[self.level]
            print("\t" * self.level,
                  "\tDone (%f sec)\n" % ((time.process_time() - ref_time) if ref_time is not None else 0.0),
                  sep="")
            if message:
                print("\t" * self.level, message, sep="")
            del self.ref_time[self.level]
            self.level -= 1

        def step(self, message=""):
            ref_time = self.ref_time[self.level]
            curr_time = time.process_time()
            if ref_time is not None:
                print("\t" * self.level, "\tDone (%f sec)\n" % (curr_time - ref_time), sep="")
            self.ref_time[self.level] = curr_time
            print("\t" * self.level, message, sep="")
else:
    class PerfMon():
        def __init__(self):
            pass

        def level_up(self, message=""):
            pass

        def level_down(self, message=""):
            pass

        def step(self, message=""):
            pass


# Scale/unit mess. FBX can store the 'reference' unit of a file in its UnitScaleFactor property
# (1.0 meaning centimeter, afaik). We use that to reflect user's default unit as set in Blender with scale_length.
# However, we always get values in BU (i.e. meters), so we have to reverse-apply that scale in global matrix...
# Note that when no default unit is available, we assume 'meters' (and hence scale by 100).
def units_blender_to_fbx_factor(scene):
    return 100.0 if (scene.unit_settings.system == 'NONE') else (100.0 * scene.unit_settings.scale_length)


# Note: this could be in a utility (math.units e.g.)...

UNITS = {
    "meter": 1.0,  # Ref unit!
    "kilometer": 0.001,
    "millimeter": 1000.0,
    "foot": 1.0 / 0.3048,
    "inch": 1.0 / 0.0254,
    "turn": 1.0,  # Ref unit!
    "degree": 360.0,
    "radian": math.pi * 2.0,
    "second": 1.0,  # Ref unit!
    "ktime": FBX_KTIME,
}


def units_convertor(u_from, u_to):
    """Return a convertor between specified units."""
    conv = UNITS[u_to] / UNITS[u_from]
    return lambda v: v * conv


def units_convertor_iter(u_from, u_to):
    """Return an iterable convertor between specified units."""
    conv = units_convertor(u_from, u_to)

    def convertor(it):
        for v in it:
            yield(conv(v))

    return convertor


def matrix4_to_array(mat):
    """Concatenate matrix's columns into a single, flat tuple"""
    # blender matrix is row major, fbx is col major so transpose on write
    return tuple(f for v in mat.transposed() for f in v)


def array_to_matrix4(arr):
    """Convert a single 16-len tuple into a valid 4D Blender matrix"""
    # Blender matrix is row major, fbx is col major so transpose on read
    return Matrix(tuple(zip(*[iter(arr)]*4))).transposed()


def similar_values(v1, v2, e=1e-6):
    """Return True if v1 and v2 are nearly the same."""
    if v1 == v2:
        return True
    return ((abs(v1 - v2) / max(abs(v1), abs(v2))) <= e)


def similar_values_iter(v1, v2, e=1e-6):
    """Return True if iterables v1 and v2 are nearly the same."""
    if v1 == v2:
        return True
    for v1, v2 in zip(v1, v2):
        if (v1 != v2) and ((abs(v1 - v2) / max(abs(v1), abs(v2))) > e):
            return False
    return True

def vcos_transformed_gen(raw_cos, m=None):
    # Note: we could most likely get much better performances with numpy, but will leave this as TODO for now.
    gen = zip(*(iter(raw_cos),) * 3)
    return gen if m is None else (m * Vector(v) for v in gen)

def nors_transformed_gen(raw_nors, m=None):
    # Great, now normals are also expected 4D!
    # XXX Back to 3D normals for now!
    # gen = zip(*(iter(raw_nors),) * 3 + (_infinite_gen(1.0),))
    gen = zip(*(iter(raw_nors),) * 3)
    return gen if m is None else (m * Vector(v) for v in gen)


# ##### UIDs code. #####

# ID class (mere int).
class UUID(int):
    pass


# UIDs storage.
_keys_to_uuids = {}
_uuids_to_keys = {}


def _key_to_uuid(uuids, key):
    # TODO: Check this is robust enough for our needs!
    # Note: We assume we have already checked the related key wasn't yet in _keys_to_uids!
    #       As int64 is signed in FBX, we keep uids below 2**63...
    if isinstance(key, int) and 0 <= key < 2**63:
        # We can use value directly as id!
        uuid = key
    else:
        uuid = hash(key)
        if uuid < 0:
            uuid = -uuid
        if uuid >= 2**63:
            uuid //= 2
    # Try to make our uid shorter!
    if uuid > int(1e9):
        t_uuid = uuid % int(1e9)
        if t_uuid not in uuids:
            uuid = t_uuid
    # Make sure our uuid *is* unique.
    if uuid in uuids:
        inc = 1 if uuid < 2**62 else -1
        while uuid in uuids:
            uuid += inc
            if 0 > uuid >= 2**63:
                # Note that this is more that unlikely, but does not harm anyway...
                raise ValueError("Unable to generate an UUID for key {}".format(key))
    return UUID(uuid)


def get_fbx_uuid_from_key(key):
    """
    Return an UUID for given key, which is assumed hasable.
    """
    uuid = _keys_to_uuids.get(key, None)
    if uuid is None:
        uuid = _key_to_uuid(_uuids_to_keys, key)
        _keys_to_uuids[key] = uuid
        _uuids_to_keys[uuid] = key
    return uuid


# XXX Not sure we'll actually need this one?
def get_key_from_fbx_uuid(uuid):
    """
    Return the key which generated this uid.
    """
    assert(uuid.__class__ == UUID)
    return _uuids_to_keys.get(uuid, None)

# ##### Element generators. #####

# Note: elem may be None, in this case the element is not added to any parent.
def elem_empty(elem, name):
    sub_elem = encode_bin.FBXElem(name)
    if elem is not None:
        elem.elems.append(sub_elem)
    return sub_elem


def _elem_data_single(elem, name, value, func_name):
    sub_elem = elem_empty(elem, name)
    getattr(sub_elem, func_name)(value)
    return sub_elem


def _elem_data_vec(elem, name, value, func_name):
    sub_elem = elem_empty(elem, name)
    func = getattr(sub_elem, func_name)
    for v in value:
        func(v)
    return sub_elem

def get_child_element(parentelem, name):
    for child in parentelem.elems:
        if child.id == name:
            return child
    return None

def elem_data_single_bool(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bool")


def elem_data_single_int16(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int16")


def elem_data_single_int32(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int32")


def elem_data_single_int64(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int64")


def elem_data_single_float32(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float32")


def elem_data_single_float64(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float64")


def elem_data_single_bytes(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bytes")


def elem_data_single_string(elem, name, value):
    return _elem_data_single(elem, name, value, "add_string")


def elem_data_single_string_unicode(elem, name, value):
    return _elem_data_single(elem, name, value, "add_string_unicode")


def elem_data_single_bool_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bool_array")


def elem_data_single_int32_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int32_array")


def elem_data_single_int64_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int64_array")


def elem_data_single_float32_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float32_array")


def elem_data_single_float64_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float64_array")


def elem_data_single_byte_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_byte_array")


def elem_data_vec_float64(elem, name, value):
    return _elem_data_vec(elem, name, value, "add_float64")


# ##### Generators for standard FBXProperties70 properties. #####

def elem_properties(elem):
    return elem_empty(elem, b"Properties70")


# Properties definitions, format: (b"type_1", b"label(???)", "name_set_value_1", "name_set_value_2", ...)
# XXX Looks like there can be various variations of formats here... Will have to be checked ultimately!
#     Also, those "custom" types like 'FieldOfView' or 'Lcl Translation' are pure nonsense,
#     these are just Vector3D ultimately... *sigh* (again).
FBX_PROPERTIES_DEFINITIONS = {
    # Generic types.
    "p_bool": (b"bool", b"", "add_int32"),  # Yes, int32 for a bool (and they do have a core bool type)!!!
    "p_integer": (b"int", b"Integer", "add_int32"),
    "p_ulonglong": (b"ULongLong", b"", "add_int64"),
    "p_double": (b"double", b"Number", "add_float64"),  # Non-animatable?
    "p_number": (b"Number", b"", "add_float64"),  # Animatable-only?
    "p_enum": (b"enum", b"", "add_int32"),
    "p_vector_3d": (b"Vector3D", b"Vector", "add_float64", "add_float64", "add_float64"),  # Non-animatable?
    "p_vector": (b"Vector", b"", "add_float64", "add_float64", "add_float64"),  # Animatable-only?
    "p_color_rgb": (b"ColorRGB", b"Color", "add_float64", "add_float64", "add_float64"),  # Non-animatable?
    "p_color": (b"Color", b"", "add_float64", "add_float64", "add_float64"),  # Animatable-only?
    "p_string": (b"KString", b"", "add_string_unicode"),
    "p_string_url": (b"KString", b"Url", "add_string_unicode"),
    "p_timestamp": (b"KTime", b"Time", "add_int64"),
    "p_datetime": (b"DateTime", b"", "add_string_unicode"),
    # Special types.
    "p_object": (b"object", b""),  # XXX Check this! No value for this prop??? Would really like to know how it works!
    "p_compound": (b"Compound", b""),
    # Specific types (sic).
    # ## Objects (Models).
    "p_lcl_translation": (b"Lcl Translation", b"", "add_float64", "add_float64", "add_float64"),
    "p_lcl_rotation": (b"Lcl Rotation", b"", "add_float64", "add_float64", "add_float64"),
    "p_lcl_scaling": (b"Lcl Scaling", b"", "add_float64", "add_float64", "add_float64"),
    "p_visibility": (b"Visibility", b"", "add_float64"),
    "p_visibility_inheritance": (b"Visibility Inheritance", b"", "add_int32"),
    # ## Cameras!!!
    "p_roll": (b"Roll", b"", "add_float64"),
    "p_opticalcenterx": (b"OpticalCenterX", b"", "add_float64"),
    "p_opticalcentery": (b"OpticalCenterY", b"", "add_float64"),
    "p_fov": (b"FieldOfView", b"", "add_float64"),
    "p_fov_x": (b"FieldOfViewX", b"", "add_float64"),
    "p_fov_y": (b"FieldOfViewY", b"", "add_float64"),
}


def _elem_props_set(elem, ptype, name, value, flags):
    p = elem_data_single_string(elem, b"P", name)
    for t in ptype[:2]:
        p.add_string(t)
    p.add_string(flags)
    if len(ptype) == 3:
        getattr(p, ptype[2])(value)
    elif len(ptype) > 3:
        # We assume value is iterable, else it's a bug!
        for callback, val in zip(ptype[2:], value):
            getattr(p, callback)(val)


def _elem_props_flags(animatable, animated, custom):
    # XXX: There are way more flags, see
    #      http://help.autodesk.com/view/FBX/2015/ENU/?guid=__cpp_ref_class_fbx_property_flags_html
    #      Unfortunately, as usual, no doc at all about their 'translation' in actual FBX file format.
    #      Curse you-know-who.
    if animatable:
        if animated:
            if custom:
                return b"A+U"
            return b"A+"
        if custom:
            return b"AU"
        return b"A"
    if custom:
        return b"U"
    return b""


def elem_props_set(elem, ptype, name, value=None, animatable=False, animated=False, custom=False):
    ptype = FBX_PROPERTIES_DEFINITIONS[ptype]
    import log
    log.debug('propset %s %s %s', str(name), str(value), type(value))
    _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, animated, custom))


def elem_props_compound(elem, cmpd_name, custom=False):
    def _setter(ptype, name, value, animatable=False, animated=False, custom=False):
        name = cmpd_name + b"|" + name
        elem_props_set(elem, ptype, name, value, animatable=animatable, animated=animated, custom=custom)

    elem_props_set(elem, "p_compound", cmpd_name, custom=custom)
    return _setter


def elem_props_template_init(templates, template_type):
    """
    Init a writing template of given type, for *one* element's properties.
    """
    ret = OrderedDict()
    tmpl = templates.get(template_type)
    if tmpl is not None:
        written = tmpl.written[0]
        props = tmpl.properties
        ret = OrderedDict((name, [val, ptype, anim, written]) for name, (val, ptype, anim) in props.items())
    return ret


def elem_props_template_set(template, elem, ptype_name, name, value, animatable=False, animated=False):
    """
    Only add a prop if the same value is not already defined in given template.
    Note it is important to not give iterators as value, here!
    """
    ptype = FBX_PROPERTIES_DEFINITIONS[ptype_name]
    if len(ptype) > 3:
        value = tuple(value)
    tmpl_val, tmpl_ptype, tmpl_animatable, tmpl_written = template.get(name, (None, None, False, False))
    # Note animatable flag from template takes precedence over given one, if applicable.
    # However, animated properties are always written, since they cannot match their template!
    if tmpl_ptype is not None and not animated:
        if (tmpl_written and
            ((len(ptype) == 3 and (tmpl_val, tmpl_ptype) == (value, ptype_name)) or
             (len(ptype) > 3 and (tuple(tmpl_val), tmpl_ptype) == (value, ptype_name)))):
            return  # Already in template and same value.
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(tmpl_animatable, animated, False))
        template[name][3] = True
    else:
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, animated, False))


def elem_props_template_finalize(template, elem):
    """
    Finalize one element's template/props.
    Issue is, some templates might be "needed" by different types (e.g. NodeAttribute is for lights, cameras, etc.),
    but values for only *one* subtype can be written as template. So we have to be sure we write those for the other
    subtypes in each and every elements, if they are not overriden by that element.
    Yes, hairy, FBX that is to say. When they could easily support several subtypes per template... :(
    """
    for name, (value, ptype_name, animatable, written) in template.items():
        if written:
            continue
        ptype = FBX_PROPERTIES_DEFINITIONS[ptype_name]
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, False, False))


# ##### Templates #####
# TODO: check all those "default" values, they should match Blender's default as much as possible, I guess?

FBXTemplate = namedtuple("FBXTemplate", ("type_name", "prop_type_name", "properties", "nbr_users", "written"))

def get_properties(properties):
    for p in properties:
        if len(p) < 3:
            continue
        if len(p) == 3:
            name, ptype, value = p
            animatable = False
            custom = False
        elif len(p) == 4:
            name, ptype, value, animatable = p
            custom = False
        else:
            name, ptype, value, animatable, custom = p

        yield (name, ptype, value, animatable, custom)

def fbx_template_generate(definitionsNode, objectType_name, users_count, propertyTemplate_name=None, properties=[]):
    template = elem_data_single_string(definitionsNode, b"ObjectType", objectType_name)
    elem_data_single_int32(template, b"Count", users_count)

    if propertyTemplate_name and len(properties) > 0:
        elem = elem_data_single_string(template, b"PropertyTemplate", propertyTemplate_name)
        props = elem_properties(elem)

        for name, ptype, value, animatable, custom in get_properties(properties):
            print(props)
            print(ptype)
            print(name)
            print(value)
            print(animatable)
            elem_props_set(props, ptype, name, value, animatable, custom)
            #try:
            #
            #except Exception as e:
            #    import log
            #    log.debug("FBX: Failed to write template prop (%r) (%s)", e, str((props, ptype, name, value, animatable)))

def fbx_templates_generate(root, fbx_templates):
    # We may have to gather different templates in the same node (e.g. NodeAttribute template gathers properties
    # for Lights, Cameras, LibNodes, etc.).
    ref_templates = {(tmpl.type_name, tmpl.prop_type_name): tmpl for tmpl in fbx_templates.values()}

    templates = OrderedDict()
    for type_name, prop_type_name, properties, nbr_users, _written in fbx_templates.values():
        tmpl = templates.get(type_name)
        if tmpl is None:
            templates[type_name] = [OrderedDict(((prop_type_name, (properties, nbr_users)),)), nbr_users]
        else:
            tmpl[0][prop_type_name] = (properties, nbr_users)
            tmpl[1] += nbr_users

    for type_name, (subprops, nbr_users) in templates.items():
        template = elem_data_single_string(root, b"ObjectType", type_name)
        elem_data_single_int32(template, b"Count", nbr_users)

        if len(subprops) == 1:
            prop_type_name, (properties, _nbr_sub_type_users) = next(iter(subprops.items()))
            subprops = (prop_type_name, properties)
            ref_templates[(type_name, prop_type_name)].written[0] = True
        else:
            # Ack! Even though this could/should work, looks like it is not supported. So we have to chose one. :|
            max_users = max_props = -1
            written_prop_type_name = None
            for prop_type_name, (properties, nbr_sub_type_users) in subprops.items():
                if nbr_sub_type_users > max_users or (nbr_sub_type_users == max_users and len(properties) > max_props):
                    max_users = nbr_sub_type_users
                    max_props = len(properties)
                    written_prop_type_name = prop_type_name
            subprops = (written_prop_type_name, properties)
            ref_templates[(type_name, written_prop_type_name)].written[0] = True

        prop_type_name, properties = subprops
        if prop_type_name and properties:
            elem = elem_data_single_string(template, b"PropertyTemplate", prop_type_name)
            props = elem_properties(elem)
            for name, (value, ptype, animatable) in properties.items():
                try:
                    elem_props_set(props, ptype, name, value, animatable=animatable)
                except Exception as e:
                    print("Failed to write template prop (%r)" % e)
                    print(props, ptype, name, value, animatable)


def fbx_name_class(name, cls):
    return FBX_NAME_CLASS_SEP.join((name, cls))


# ##### Top-level FBX data container. #####

# Helper sub-container gathering all exporter settings related to media (texture files).
FBXExportSettingsMedia = namedtuple("FBXExportSettingsMedia", (
    "path_mode", "base_src", "base_dst", "subdir",
    "embed_textures", "copy_set", "embedded_set",
))

# Helper container gathering all exporter settings.
FBXExportSettings = namedtuple("FBXExportSettings", (
    "report", "to_axes", "global_matrix", "global_scale", "apply_unit_scale", "unit_scale",
    "bake_space_transform", "global_matrix_inv", "global_matrix_inv_transposed",
    "context_objects", "object_types", "use_mesh_modifiers", "use_mesh_modifiers_render",
    "mesh_smooth_type", "use_mesh_edges", "use_tspace",
    "armature_nodetype", "use_armature_deform_only", "add_leaf_bones",
    "bone_correction_matrix", "bone_correction_matrix_inv",
    "bake_anim", "bake_anim_use_all_bones", "bake_anim_use_nla_strips", "bake_anim_use_all_actions",
    "bake_anim_step", "bake_anim_simplify_factor", "bake_anim_force_startend_keying",
    "use_metadata", "media_settings", "use_custom_props",
))

# Helper container gathering some data we need multiple times:
#     * templates.
#     * settings, scene.
#     * objects.
#     * object data.
#     * skinning data (binding armature/mesh).
#     * animations.
FBXExportData = namedtuple("FBXExportData", (
    "templates", "templates_users", "connections",
    "settings", "scene", "objects", "animations", "animated", "frame_start", "frame_end",
    "data_empties", "data_lamps", "data_cameras", "data_meshes", "mesh_mat_indices",
    "data_bones", "data_leaf_bones", "data_deformers_skin", "data_deformers_shape",
    "data_world", "data_materials", "data_textures", "data_videos",
))

# Helper container gathering all importer settings.
FBXImportSettings = namedtuple("FBXImportSettings", (
    "report", "to_axes", "global_matrix", "global_scale",
    "bake_space_transform", "global_matrix_inv", "global_matrix_inv_transposed",
    "use_custom_normals", "use_cycles", "use_image_search",
    "use_alpha_decals", "decal_offset",
    "use_anim", "anim_offset",
    "use_custom_props", "use_custom_props_enum_as_string",
    "cycles_material_wrap_map", "image_cache",
    "ignore_leaf_bones", "force_connect_children", "automatic_bone_orientation", "bone_correction_matrix",
    "use_prepost_rot",
))
