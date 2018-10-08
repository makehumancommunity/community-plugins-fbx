def fbx_data_video_elements(root, vid, scene_data):
    """
    Write the actual image data block.
    """
    msetts = scene_data.settings.media_settings

    vid_key, _texs = scene_data.data_videos[vid]
    fname_abs, fname_rel = _gen_vid_path(vid, scene_data)

    fbx_vid = elem_data_single_int64(root, b"Video", get_fbx_uuid_from_key(vid_key))
    fbx_vid.add_string(fbx_name_class(vid.name.encode(), b"Video"))
    fbx_vid.add_string(b"Clip")

    elem_data_single_string(fbx_vid, b"Type", b"Clip")
    # XXX No Version???

    tmpl = elem_props_template_init(scene_data.templates, b"Video")
    props = elem_properties(fbx_vid)
    elem_props_template_set(tmpl, props, "p_string_url", b"Path", fname_abs)
    elem_props_template_finalize(tmpl, props)

    elem_data_single_int32(fbx_vid, b"UseMipMap", 0)
    elem_data_single_string_unicode(fbx_vid, b"Filename", fname_abs)
    elem_data_single_string_unicode(fbx_vid, b"RelativeFilename", fname_rel)

    if scene_data.settings.media_settings.embed_textures:
        if vid.packed_file is not None:
            # We only ever embed a given file once!
            if fname_abs not in msetts.embedded_set:
                elem_data_single_bytes(fbx_vid, b"Content", vid.packed_file.data)
                msetts.embedded_set.add(fname_abs)
        else:
            filepath = bpy.path.abspath(vid.filepath)
            # We only ever embed a given file once!
            if filepath not in msetts.embedded_set:
                try:
                    with open(filepath, 'br') as f:
                        elem_data_single_bytes(fbx_vid, b"Content", f.read())
                except Exception as e:
                    print("WARNING: embedding file {} failed ({})".format(filepath, e))
                    elem_data_single_bytes(fbx_vid, b"Content", b"")
                msetts.embedded_set.add(filepath)
    # Looks like we'd rather not write any 'Content' element in this case (see T44442).
    # Sounds suspect, but let's try it!
    #~ else:
        #~ elem_data_single_bytes(fbx_vid, b"Content", b"")


