def fbx_data_skeleton_bone_node(objectsParent, key, id, properties):
    # Bone "data".

    #id = get_fbx_uuid_from_key(boneDataKey)

    fbx_bo = elem_data_single_int64(objectsParent, b"NodeAttribute", id)
    fbx_bo.add_string(fbx_name_class(key.encode()))
    fbx_bo.add_string(b"LimbNode")
    elem_data_single_string(fbx_bo, b"TypeFlags", b"Skeleton")

    props = elem_properties(fbx_bo)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)


