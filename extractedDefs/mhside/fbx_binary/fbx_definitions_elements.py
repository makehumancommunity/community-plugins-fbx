def fbx_definitions_elements(root, users_count):
    """
    Templates definitions. Only used by Objects data afaik (apart from dummy GlobalSettings one).
    """
    definitions = elem_empty(root, b"Definitions")

    elem_data_single_int32(definitions, b"Version", FBX_TEMPLATES_VERSION)
    elem_data_single_int32(definitions, b"Count", users_count)

    fbx_template_generate(definitions, b"GlobalSettings", 1)
    #fbx_templates_generate(definitions, scene_data.templates)


