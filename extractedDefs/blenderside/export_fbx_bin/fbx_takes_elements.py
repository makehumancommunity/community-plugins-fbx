def fbx_takes_elements(root, scene_data):
    """
    Animations.
    """
    # XXX Pretty sure takes are no more needed...
    takes = elem_empty(root, b"Takes")
    elem_data_single_string(takes, b"Current", b"")

    animations = scene_data.animations
    for astack_key, animations, alayer_key, name, f_start, f_end in animations:
        scene = scene_data.scene
        fps = scene.render.fps / scene.render.fps_base
        start_ktime = int(convert_sec_to_ktime(f_start / fps))
        end_ktime = int(convert_sec_to_ktime(f_end / fps))

        take = elem_data_single_string(takes, b"Take", name)
        elem_data_single_string(take, b"FileName", name + b".tak")
        take_loc_time = elem_data_single_int64(take, b"LocalTime", start_ktime)
        take_loc_time.add_int64(end_ktime)
        take_ref_time = elem_data_single_int64(take, b"ReferenceTime", start_ktime)
        take_ref_time.add_int64(end_ktime)


