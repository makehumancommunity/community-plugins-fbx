def fbx_data_leaf_bone_elements(root, scene_data):
    # Write a dummy leaf bone that is used by applications to show the length of the last bone in a chain
    for (node_name, _par_uuid, node_uuid, attr_uuid, matrix, hide, size) in scene_data.data_leaf_bones:
        # Bone 'data'...
        fbx_bo = elem_data_single_int64(root, b"NodeAttribute", attr_uuid)
        fbx_bo.add_string(fbx_name_class(node_name.encode(), b"NodeAttribute"))
        fbx_bo.add_string(b"LimbNode")
        elem_data_single_string(fbx_bo, b"TypeFlags", b"Skeleton")

        tmpl = elem_props_template_init(scene_data.templates, b"Bone")
        props = elem_properties(fbx_bo)
        elem_props_template_set(tmpl, props, "p_double", b"Size", size)
        elem_props_template_finalize(tmpl, props)

        # And bone object.
        model = elem_data_single_int64(root, b"Model", node_uuid)
        model.add_string(fbx_name_class(node_name.encode(), b"Model"))
        model.add_string(b"LimbNode")

        elem_data_single_int32(model, b"Version", FBX_MODELS_VERSION)

        # Object transform info.
        loc, rot, scale = matrix.decompose()
        rot = rot.to_euler('XYZ')
        rot = tuple(convert_rad_to_deg_iter(rot))

        tmpl = elem_props_template_init(scene_data.templates, b"Model")
        # For now add only loc/rot/scale...
        props = elem_properties(model)
        # Generated leaf bones are obviously never animated!
        elem_props_template_set(tmpl, props, "p_lcl_translation", b"Lcl Translation", loc)
        elem_props_template_set(tmpl, props, "p_lcl_rotation", b"Lcl Rotation", rot)
        elem_props_template_set(tmpl, props, "p_lcl_scaling", b"Lcl Scaling", scale)
        elem_props_template_set(tmpl, props, "p_visibility", b"Visibility", float(not hide))

        # Absolutely no idea what this is, but seems mandatory for validity of the file, and defaults to
        # invalid -1 value...
        elem_props_template_set(tmpl, props, "p_integer", b"DefaultAttributeIndex", 0)

        elem_props_template_set(tmpl, props, "p_enum", b"InheritType", 1)  # RSrs

        # Those settings would obviously need to be edited in a complete version of the exporter, may depends on
        # object type, etc.
        elem_data_single_int32(model, b"MultiLayer", 0)
        elem_data_single_int32(model, b"MultiTake", 0)
        elem_data_single_bool(model, b"Shading", True)
        elem_data_single_string(model, b"Culling", b"CullingOff")

        elem_props_template_finalize(tmpl, props)


