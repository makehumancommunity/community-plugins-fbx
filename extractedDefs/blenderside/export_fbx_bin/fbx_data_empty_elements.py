def fbx_data_empty_elements(root, empty, scene_data):
    """
    Write the Empty data block.
    """
    empty_key = scene_data.data_empties[empty]

    null = elem_data_single_int64(root, b"NodeAttribute", get_fbx_uuid_from_key(empty_key))
    null.add_string(fbx_name_class(empty.name.encode(), b"NodeAttribute"))
    null.add_string(b"Null")

    elem_data_single_string(null, b"TypeFlags", b"Null")

    tmpl = elem_props_template_init(scene_data.templates, b"Null")
    props = elem_properties(null)
    elem_props_template_finalize(tmpl, props)

    # No custom properties, already saved with object (Model).


