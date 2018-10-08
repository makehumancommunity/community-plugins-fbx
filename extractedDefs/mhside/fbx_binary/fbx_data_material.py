def fbx_data_material(objectsParent, key, id, properties):
    fbx_mat = elem_data_single_int64(objectsParent, b"Material", id)
    fbx_mat.add_string(fbx_name_class(key))
    fbx_mat.add_string(b"")

    elem_data_single_int32(fbx_mat, b"Version", 102)
    elem_data_single_string(fbx_mat, b"ShadingModel", "phong")
    elem_data_single_int32(fbx_mat, b"MultiLayer", 0)

    props = elem_properties(fbx_mat)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)


