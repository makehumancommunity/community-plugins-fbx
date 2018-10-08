def fbx_data_object_elements(root, ob_obj, scene_data):
    """
    Write the Object (Model) data blocks.
    Note this "Model" can also be bone or dupli!
    """
    obj_type = b"Null"  # default, sort of empty...
    if ob_obj.is_bone:
        obj_type = b"LimbNode"
    elif (ob_obj.type == 'ARMATURE'):
        if scene_data.settings.armature_nodetype == 'ROOT':
            obj_type = b"Root"
        elif scene_data.settings.armature_nodetype == 'LIMBNODE':
            obj_type = b"LimbNode"
        else:  # Default, preferred option...
            obj_type = b"Null"
    elif (ob_obj.type in BLENDER_OBJECT_TYPES_MESHLIKE):
        obj_type = b"Mesh"
    elif (ob_obj.type == 'LAMP'):
        obj_type = b"Light"
    elif (ob_obj.type == 'CAMERA'):
        obj_type = b"Camera"
    model = elem_data_single_int64(root, b"Model", ob_obj.fbx_uuid)
    model.add_string(fbx_name_class(ob_obj.name.encode(), b"Model"))
    model.add_string(obj_type)

    elem_data_single_int32(model, b"Version", FBX_MODELS_VERSION)

    # Object transform info.
    loc, rot, scale, matrix, matrix_rot = ob_obj.fbx_object_tx(scene_data)
    rot = tuple(convert_rad_to_deg_iter(rot))

    tmpl = elem_props_template_init(scene_data.templates, b"Model")
    # For now add only loc/rot/scale...
    props = elem_properties(model)
    elem_props_template_set(tmpl, props, "p_lcl_translation", b"Lcl Translation", loc,
                            animatable=True, animated=((ob_obj.key, "Lcl Translation") in scene_data.animated))
    elem_props_template_set(tmpl, props, "p_lcl_rotation", b"Lcl Rotation", rot,
                            animatable=True, animated=((ob_obj.key, "Lcl Rotation") in scene_data.animated))
    elem_props_template_set(tmpl, props, "p_lcl_scaling", b"Lcl Scaling", scale,
                            animatable=True, animated=((ob_obj.key, "Lcl Scaling") in scene_data.animated))
    elem_props_template_set(tmpl, props, "p_visibility", b"Visibility", float(not ob_obj.hide))

    # Absolutely no idea what this is, but seems mandatory for validity of the file, and defaults to
    # invalid -1 value...
    elem_props_template_set(tmpl, props, "p_integer", b"DefaultAttributeIndex", 0)

    elem_props_template_set(tmpl, props, "p_enum", b"InheritType", 1)  # RSrs

    # Custom properties.
    if scene_data.settings.use_custom_props:
        fbx_data_element_custom_properties(props, ob_obj.bdata)

    # Those settings would obviously need to be edited in a complete version of the exporter, may depends on
    # object type, etc.
    elem_data_single_int32(model, b"MultiLayer", 0)
    elem_data_single_int32(model, b"MultiTake", 0)
    elem_data_single_bool(model, b"Shading", True)
    elem_data_single_string(model, b"Culling", b"CullingOff")

    if obj_type == b"Camera":
        # Why, oh why are FBX cameras such a mess???
        # And WHY add camera data HERE??? Not even sure this is needed...
        render = scene_data.scene.render
        width = render.resolution_x * 1.0
        height = render.resolution_y * 1.0
        elem_props_template_set(tmpl, props, "p_enum", b"ResolutionMode", 0)  # Don't know what it means
        elem_props_template_set(tmpl, props, "p_double", b"AspectW", width)
        elem_props_template_set(tmpl, props, "p_double", b"AspectH", height)
        elem_props_template_set(tmpl, props, "p_bool", b"ViewFrustum", True)
        elem_props_template_set(tmpl, props, "p_enum", b"BackgroundMode", 0)  # Don't know what it means
        elem_props_template_set(tmpl, props, "p_bool", b"ForegroundTransparent", True)

    elem_props_template_finalize(tmpl, props)


