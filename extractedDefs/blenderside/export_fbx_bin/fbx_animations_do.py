def fbx_animations_do(scene_data, ref_id, f_start, f_end, start_zero, objects=None, force_keep=False):
    """
    Generate animation data (a single AnimStack) from objects, for a given frame range.
    """
    bake_step = scene_data.settings.bake_anim_step
    simplify_fac = scene_data.settings.bake_anim_simplify_factor
    scene = scene_data.scene
    force_keying = scene_data.settings.bake_anim_use_all_bones
    force_sek = scene_data.settings.bake_anim_force_startend_keying

    if objects is not None:
        # Add bones and duplis!
        for ob_obj in tuple(objects):
            if not ob_obj.is_object:
                continue
            if ob_obj.type == 'ARMATURE':
                objects |= {bo_obj for bo_obj in ob_obj.bones if bo_obj in scene_data.objects}
            ob_obj.dupli_list_create(scene, 'RENDER')
            for dp_obj in ob_obj.dupli_list:
                if dp_obj in scene_data.objects:
                    objects.add(dp_obj)
            ob_obj.dupli_list_clear()
    else:
        objects = scene_data.objects

    back_currframe = scene.frame_current
    animdata_ob = OrderedDict()
    p_rots = {}

    for ob_obj in objects:
        if ob_obj.parented_to_armature:
            continue
        ACNW = AnimationCurveNodeWrapper
        loc, rot, scale, _m, _mr = ob_obj.fbx_object_tx(scene_data)
        rot_deg = tuple(convert_rad_to_deg_iter(rot))
        force_key = (simplify_fac == 0.0) or (ob_obj.is_bone and force_keying)
        animdata_ob[ob_obj] = (ACNW(ob_obj.key, 'LCL_TRANSLATION', force_key, force_sek, loc),
                               ACNW(ob_obj.key, 'LCL_ROTATION', force_key, force_sek, rot_deg),
                               ACNW(ob_obj.key, 'LCL_SCALING', force_key, force_sek, scale))
        p_rots[ob_obj] = rot

    animdata_shapes = OrderedDict()
    force_key = (simplify_fac == 0.0)
    for me, (me_key, _shapes_key, shapes) in scene_data.data_deformers_shape.items():
        # Ignore absolute shape keys for now!
        if not me.shape_keys.use_relative:
            continue
        for shape, (channel_key, geom_key, _shape_verts_co, _shape_verts_idx) in shapes.items():
            acnode = AnimationCurveNodeWrapper(channel_key, 'SHAPE_KEY', force_key, force_sek, (0.0,))
            # Sooooo happy to have to twist again like a mad snake... Yes, we need to write those curves twice. :/
            acnode.add_group(me_key, shape.name, shape.name, (shape.name,))
            animdata_shapes[channel_key] = (acnode, me, shape)

    currframe = f_start
    while currframe <= f_end:
        real_currframe = currframe - f_start if start_zero else currframe
        scene.frame_set(int(currframe), currframe - int(currframe))

        for ob_obj in animdata_ob:
            ob_obj.dupli_list_create(scene, 'RENDER')
        for ob_obj, (anim_loc, anim_rot, anim_scale) in animdata_ob.items():
            # We compute baked loc/rot/scale for all objects (rot being euler-compat with previous value!).
            p_rot = p_rots.get(ob_obj, None)
            loc, rot, scale, _m, _mr = ob_obj.fbx_object_tx(scene_data, rot_euler_compat=p_rot)
            p_rots[ob_obj] = rot
            anim_loc.add_keyframe(real_currframe, loc)
            anim_rot.add_keyframe(real_currframe, tuple(convert_rad_to_deg_iter(rot)))
            anim_scale.add_keyframe(real_currframe, scale)
        for ob_obj in objects:
            ob_obj.dupli_list_clear()
        for anim_shape, me, shape in animdata_shapes.values():
            anim_shape.add_keyframe(real_currframe, (shape.value * 100.0,))
        currframe += bake_step

    scene.frame_set(back_currframe, 0.0)

    animations = OrderedDict()

    # And now, produce final data (usable by FBX export code)
    # Objects-like loc/rot/scale...
    for ob_obj, anims in animdata_ob.items():
        for anim in anims:
            anim.simplify(simplify_fac, bake_step, force_keep)
            if not anim:
                continue
            for obj_key, group_key, group, fbx_group, fbx_gname in anim.get_final_data(scene, ref_id, force_keep):
                anim_data = animations.get(obj_key)
                if anim_data is None:
                    anim_data = animations[obj_key] = ("dummy_unused_key", OrderedDict())
                anim_data[1][fbx_group] = (group_key, group, fbx_gname)

    # And meshes' shape keys.
    for channel_key, (anim_shape, me, shape) in animdata_shapes.items():
        final_keys = OrderedDict()
        anim_shape.simplify(simplify_fac, bake_step, force_keep)
        if not anim_shape:
            continue
        for elem_key, group_key, group, fbx_group, fbx_gname in anim_shape.get_final_data(scene, ref_id, force_keep):
                anim_data = animations.get(elem_key)
                if anim_data is None:
                    anim_data = animations[elem_key] = ("dummy_unused_key", OrderedDict())
                anim_data[1][fbx_group] = (group_key, group, fbx_gname)

    astack_key = get_blender_anim_stack_key(scene, ref_id)
    alayer_key = get_blender_anim_layer_key(scene, ref_id)
    name = (get_blenderID_name(ref_id) if ref_id else scene.name).encode()

    if start_zero:
        f_end -= f_start
        f_start = 0.0

    return (astack_key, animations, alayer_key, name, f_start, f_end) if animations else None


