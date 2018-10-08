def fbx_data_texture_file_element(objectsParent, key, id, video_key, video_id, texpath, texpath_rel, properties_tex, properties_vid):
    """
    Write the (file) Texture data block.
    """
    # XXX All this is very fuzzy to me currently...
    #     Textures do not seem to use properties as much as they could.
    #     For now assuming most logical and simple stuff.

    fbx_vid = elem_data_single_int64(objectsParent, b"Video", video_id)
    fbx_vid.add_string(fbx_name_class(video_key.encode()))
    fbx_vid.add_string(b"Clip")

    props = elem_properties(fbx_vid)
    for pname, ptype, value, animatable, custom in get_properties(properties_vid):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    elem_data_single_int32(fbx_vid, b"UseMipMap", 0)
    elem_data_single_string_unicode(fbx_vid, b"Filename", texpath)
    elem_data_single_string_unicode(fbx_vid, b"RelativeFilename", texpath_rel)


    fbx_tex = elem_data_single_int64(objectsParent, b"Texture", id)
    fbx_tex.add_string(fbx_name_class(key.encode()))
    fbx_tex.add_string(b"")

    elem_data_single_string(fbx_tex, b"Type", b"TextureVideoClip")
    elem_data_single_int32(fbx_tex, b"Version", FBX_TEXTURE_VERSION)
    elem_data_single_string(fbx_tex, b"TextureName", fbx_name_class(key.encode()))
    elem_data_single_string(fbx_tex, b"Media", video_key)
    elem_data_single_string_unicode(fbx_tex, b"Filename", texpath)
    elem_data_single_string_unicode(fbx_tex, b"RelativeFilename", texpath_rel)

    elem_data_single_float32_array(fbx_tex, b"ModelUVTranslation", [0,0])
    elem_data_single_float32_array(fbx_tex, b"ModelUVScaling", [1,1])
    elem_data_single_string(fbx_tex, b"Texture_Alpha_Source", "None")
    elem_data_single_int32_array(fbx_tex, b"Cropping", [0,0,0,0])

    props = elem_properties(fbx_tex)
    for pname, ptype, value, animatable, custom in get_properties(properties_tex):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    # UseMaterial should always be ON imho.
    elem_props_set(props, "p_bool", b"UseMaterial", True)


