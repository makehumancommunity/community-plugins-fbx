def fbx_data_animation_elements(root, scene_data):
    """
    Write animation data.
    """
    animations = scene_data.animations
    if not animations:
        return
    scene = scene_data.scene

    fps = scene.render.fps / scene.render.fps_base

    def keys_to_ktimes(keys):
        return (int(v) for v in convert_sec_to_ktime_iter((f / fps for f, _v in keys)))

    # Animation stacks.
    for astack_key, alayers, alayer_key, name, f_start, f_end in animations:
        astack = elem_data_single_int64(root, b"AnimationStack", get_fbx_uuid_from_key(astack_key))
        astack.add_string(fbx_name_class(name, b"AnimStack"))
        astack.add_string(b"")

        astack_tmpl = elem_props_template_init(scene_data.templates, b"AnimationStack")
        astack_props = elem_properties(astack)
        r = scene_data.scene.render
        fps = r.fps / r.fps_base
        start = int(convert_sec_to_ktime(f_start / fps))
        end = int(convert_sec_to_ktime(f_end / fps))
        elem_props_template_set(astack_tmpl, astack_props, "p_timestamp", b"LocalStart", start)
        elem_props_template_set(astack_tmpl, astack_props, "p_timestamp", b"LocalStop", end)
        elem_props_template_set(astack_tmpl, astack_props, "p_timestamp", b"ReferenceStart", start)
        elem_props_template_set(astack_tmpl, astack_props, "p_timestamp", b"ReferenceStop", end)
        elem_props_template_finalize(astack_tmpl, astack_props)

        # For now, only one layer for all animations.
        alayer = elem_data_single_int64(root, b"AnimationLayer", get_fbx_uuid_from_key(alayer_key))
        alayer.add_string(fbx_name_class(name, b"AnimLayer"))
        alayer.add_string(b"")

        for ob_obj, (alayer_key, acurvenodes) in alayers.items():
            # Animation layer.
            # alayer = elem_data_single_int64(root, b"AnimationLayer", get_fbx_uuid_from_key(alayer_key))
            # alayer.add_string(fbx_name_class(ob_obj.name.encode(), b"AnimLayer"))
            # alayer.add_string(b"")

            for fbx_prop, (acurvenode_key, acurves, acurvenode_name) in acurvenodes.items():
                # Animation curve node.
                acurvenode = elem_data_single_int64(root, b"AnimationCurveNode", get_fbx_uuid_from_key(acurvenode_key))
                acurvenode.add_string(fbx_name_class(acurvenode_name.encode(), b"AnimCurveNode"))
                acurvenode.add_string(b"")

                acn_tmpl = elem_props_template_init(scene_data.templates, b"AnimationCurveNode")
                acn_props = elem_properties(acurvenode)

                for fbx_item, (acurve_key, def_value, keys, _acurve_valid) in acurves.items():
                    elem_props_template_set(acn_tmpl, acn_props, "p_number", fbx_item.encode(),
                                            def_value, animatable=True)

                    # Only create Animation curve if needed!
                    if keys:
                        acurve = elem_data_single_int64(root, b"AnimationCurve", get_fbx_uuid_from_key(acurve_key))
                        acurve.add_string(fbx_name_class(b"", b"AnimCurve"))
                        acurve.add_string(b"")

                        # key attributes...
                        nbr_keys = len(keys)
                        # flags...
                        keyattr_flags = (
                            1 << 2 |   # interpolation mode, 1 = constant, 2 = linear, 3 = cubic.
                            1 << 8 |   # tangent mode, 8 = auto, 9 = TCB, 10 = user, 11 = generic break,
                            1 << 13 |  # tangent mode, 12 = generic clamp, 13 = generic time independent,
                            1 << 14 |  # tangent mode, 13 + 14 = generic clamp progressive.
                            0,
                        )
                        # Maybe values controlling TCB & co???
                        keyattr_datafloat = (0.0, 0.0, 9.419963346924634e-30, 0.0)

                        # And now, the *real* data!
                        elem_data_single_float64(acurve, b"Default", def_value)
                        elem_data_single_int32(acurve, b"KeyVer", FBX_ANIM_KEY_VERSION)
                        elem_data_single_int64_array(acurve, b"KeyTime", keys_to_ktimes(keys))
                        elem_data_single_float32_array(acurve, b"KeyValueFloat", (v for _f, v in keys))
                        elem_data_single_int32_array(acurve, b"KeyAttrFlags", keyattr_flags)
                        elem_data_single_float32_array(acurve, b"KeyAttrDataFloat", keyattr_datafloat)
                        elem_data_single_int32_array(acurve, b"KeyAttrRefCount", (nbr_keys,))

                elem_props_template_finalize(acn_tmpl, acn_props)


