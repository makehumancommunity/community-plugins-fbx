def fbx_data_skeleton_model(objectsParent, key, id, properties):
    # Skeleton null object (has no data).

    #id = get_fbx_uuid_from_key(boneDataKey)

    fbx_bo = elem_data_single_int64(objectsParent, b"Model", id)
    fbx_bo.add_string(fbx_name_class(key.encode()))
    fbx_bo.add_string(b"Null")
    elem_data_single_int32(fbx_bo, b"Version", FBX_MODELS_VERSION)
    elem_data_single_bool(fbx_bo, b"Shading", True)
    elem_data_single_string(fbx_bo, b"Culling", "CullingOff")

    props = elem_properties(fbx_bo)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)


