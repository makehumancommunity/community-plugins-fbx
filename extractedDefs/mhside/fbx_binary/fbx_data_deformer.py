def fbx_data_deformer(objectsParent, key, id, properties):
    fbx_skin = elem_data_single_int64(objectsParent, b"Deformer", id)
    fbx_skin.add_string(fbx_name_class(key))
    fbx_skin.add_string(b"Skin")

    props = elem_properties(fbx_skin)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    elem_data_single_int32(fbx_skin, b"Version", FBX_DEFORMER_SKIN_VERSION)
    elem_data_single_float64(fbx_skin, b"Link_DeformAcuracy", 50.0)  # Only vague idea what it is...


