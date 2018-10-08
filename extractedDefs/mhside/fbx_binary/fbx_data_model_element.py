def fbx_data_model_element(objectsParent, key, id, properties):
    mod = elem_data_single_int64(objectsParent, b"Model", id)
    mod.add_string(fbx_name_class(key.encode()))
    mod.add_string(b"Mesh")

    elem_data_single_int32(mod, b"Version", FBX_MODELS_VERSION)

    props = elem_properties(mod)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    elem_data_single_string(mod, b"Shading", "Y")
    elem_data_single_string(mod, b"Culling", "CullingOff")


