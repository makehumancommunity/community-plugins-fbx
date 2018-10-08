def fbx_data_material_elements(root, mat, scene_data):
    """
    Write the Material data block.
    """
    ambient_color = (0.0, 0.0, 0.0)
    if scene_data.data_world:
        ambient_color = next(iter(scene_data.data_world.keys())).ambient_color

    mat_key, _objs = scene_data.data_materials[mat]
    skip_mat = check_skip_material(mat)
    mat_type = b"Phong"
    # Approximation...
    if not skip_mat and mat.specular_shader not in {'COOKTORR', 'PHONG', 'BLINN'}:
        mat_type = b"Lambert"

    fbx_mat = elem_data_single_int64(root, b"Material", get_fbx_uuid_from_key(mat_key))
    fbx_mat.add_string(fbx_name_class(mat.name.encode(), b"Material"))
    fbx_mat.add_string(b"")

    elem_data_single_int32(fbx_mat, b"Version", FBX_MATERIAL_VERSION)
    # those are not yet properties, it seems...
    elem_data_single_string(fbx_mat, b"ShadingModel", mat_type)
    elem_data_single_int32(fbx_mat, b"MultiLayer", 0)  # Should be bool...

    tmpl = elem_props_template_init(scene_data.templates, b"Material")
    props = elem_properties(fbx_mat)

    if not skip_mat:
        elem_props_template_set(tmpl, props, "p_string", b"ShadingModel", mat_type.decode())
        elem_props_template_set(tmpl, props, "p_color", b"EmissiveColor", mat.diffuse_color)
        elem_props_template_set(tmpl, props, "p_number", b"EmissiveFactor", mat.emit)
        elem_props_template_set(tmpl, props, "p_color", b"AmbientColor", ambient_color)
        elem_props_template_set(tmpl, props, "p_number", b"AmbientFactor", mat.ambient)
        elem_props_template_set(tmpl, props, "p_color", b"DiffuseColor", mat.diffuse_color)
        elem_props_template_set(tmpl, props, "p_number", b"DiffuseFactor", mat.diffuse_intensity)
        elem_props_template_set(tmpl, props, "p_color", b"TransparentColor",
                                mat.diffuse_color if mat.use_transparency else (1.0, 1.0, 1.0))
        elem_props_template_set(tmpl, props, "p_number", b"TransparencyFactor",
                                1.0 - mat.alpha if mat.use_transparency else 0.0)
        elem_props_template_set(tmpl, props, "p_number", b"Opacity", mat.alpha if mat.use_transparency else 1.0)
        elem_props_template_set(tmpl, props, "p_vector_3d", b"NormalMap", (0.0, 0.0, 0.0))
        # Not sure about those...
        """
        b"Bump": ((0.0, 0.0, 0.0), "p_vector_3d"),
        b"BumpFactor": (1.0, "p_double"),
        b"DisplacementColor": ((0.0, 0.0, 0.0), "p_color_rgb"),
        b"DisplacementFactor": (0.0, "p_double"),
        """
        if mat_type == b"Phong":
            elem_props_template_set(tmpl, props, "p_color", b"SpecularColor", mat.specular_color)
            elem_props_template_set(tmpl, props, "p_number", b"SpecularFactor", mat.specular_intensity / 2.0)
            # See Material template about those two!
            elem_props_template_set(tmpl, props, "p_number", b"Shininess", (mat.specular_hardness - 1.0) / 5.10)
            elem_props_template_set(tmpl, props, "p_number", b"ShininessExponent", (mat.specular_hardness - 1.0) / 5.10)
            elem_props_template_set(tmpl, props, "p_color", b"ReflectionColor", mat.mirror_color)
            elem_props_template_set(tmpl, props, "p_number", b"ReflectionFactor",
                                    mat.raytrace_mirror.reflect_factor if mat.raytrace_mirror.use else 0.0)

    elem_props_template_finalize(tmpl, props)

    # Custom properties.
    if scene_data.settings.use_custom_props:
        fbx_data_element_custom_properties(props, mat)


