def fbx_animations(scene_data):
    """
    Generate global animation data from objects.
    """
    scene = scene_data.scene
    animations = []
    animated = set()
    frame_start = 1e100
    frame_end = -1e100

    def add_anim(animations, animated, anim):
        nonlocal frame_start, frame_end
        if anim is not None:
            animations.append(anim)
            f_start, f_end = anim[4:6]
            if f_start < frame_start:
                frame_start = f_start
            if f_end > frame_end:
                frame_end = f_end

            _astack_key, astack, _alayer_key, _name, _fstart, _fend = anim
            for elem_key, (alayer_key, acurvenodes) in astack.items():
                for fbx_prop, (acurvenode_key, acurves, acurvenode_name) in acurvenodes.items():
                    animated.add((elem_key, fbx_prop))

    # Per-NLA strip animstacks.
    if scene_data.settings.bake_anim_use_nla_strips:
        strips = []
        ob_actions = []
        for ob_obj in scene_data.objects:
            # NLA tracks only for objects, not bones!
            if not ob_obj.is_object:
                continue
            ob = ob_obj.bdata  # Back to real Blender Object.
            if not ob.animation_data:
                continue
            # We have to remove active action from objects, it overwrites strips actions otherwise...
            ob_actions.append((ob, ob.animation_data.action))
            ob.animation_data.action = None
            for track in ob.animation_data.nla_tracks:
                if track.mute:
                    continue
                for strip in track.strips:
                    if strip.mute:
                        continue
                    strips.append(strip)
                    strip.mute = True

        for strip in strips:
            strip.mute = False
            add_anim(animations, animated,
                     fbx_animations_do(scene_data, strip, strip.frame_start, strip.frame_end, True, force_keep=True))
            strip.mute = True

        for strip in strips:
            strip.mute = False

        for ob, ob_act in ob_actions:
            ob.animation_data.action = ob_act

    # All actions.
    if scene_data.settings.bake_anim_use_all_actions:
        def validate_actions(act, path_resolve):
            for fc in act.fcurves:
                data_path = fc.data_path
                if fc.array_index:
                    data_path = data_path + "[%d]" % fc.array_index
                try:
                    path_resolve(data_path)
                except ValueError:
                    return False  # Invalid.
            return True  # Valid.

        def restore_object(ob_to, ob_from):
            # Restore org state of object (ugh :/ ).
            props = (
                'location', 'rotation_quaternion', 'rotation_axis_angle', 'rotation_euler', 'rotation_mode', 'scale',
                'delta_location', 'delta_rotation_euler', 'delta_rotation_quaternion', 'delta_scale',
                'lock_location', 'lock_rotation', 'lock_rotation_w', 'lock_rotations_4d', 'lock_scale',
                'tag', 'layers', 'select', 'track_axis', 'up_axis', 'active_material', 'active_material_index',
                'matrix_parent_inverse', 'empty_draw_type', 'empty_draw_size', 'empty_image_offset', 'pass_index',
                'color', 'hide', 'hide_select', 'hide_render', 'use_slow_parent', 'slow_parent_offset',
                'use_extra_recalc_object', 'use_extra_recalc_data', 'dupli_type', 'use_dupli_frames_speed',
                'use_dupli_vertices_rotation', 'use_dupli_faces_scale', 'dupli_faces_scale', 'dupli_group',
                'dupli_frames_start', 'dupli_frames_end', 'dupli_frames_on', 'dupli_frames_off',
                'draw_type', 'show_bounds', 'draw_bounds_type', 'show_name', 'show_axis', 'show_texture_space',
                'show_wire', 'show_all_edges', 'show_transparent', 'show_x_ray',
                'show_only_shape_key', 'use_shape_key_edit_mode', 'active_shape_key_index',
            )
            for p in props:
                if not ob_to.is_property_readonly(p):
                    setattr(ob_to, p, getattr(ob_from, p))

        for ob_obj in scene_data.objects:
            # Actions only for objects, not bones!
            if not ob_obj.is_object:
                continue

            ob = ob_obj.bdata  # Back to real Blender Object.

            if not ob.animation_data:
                continue  # Do not export animations for objects that are absolutely not animated, see T44386.

            if ob.animation_data.is_property_readonly('action'):
                continue  # Cannot re-assign 'active action' to this object (usually related to NLA usage, see T48089).

            # We can't play with animdata and actions and get back to org state easily.
            # So we have to add a temp copy of the object to the scene, animate it, and remove it... :/
            ob_copy = ob.copy()
            # Great, have to handle bones as well if needed...
            pbones_matrices = [pbo.matrix_basis.copy() for pbo in ob.pose.bones] if ob.type == 'ARMATURE' else ...

            org_act = ob.animation_data.action
            path_resolve = ob.path_resolve

            for act in bpy.data.actions:
                # For now, *all* paths in the action must be valid for the object, to validate the action.
                # Unless that action was already assigned to the object!
                if act != org_act and not validate_actions(act, path_resolve):
                    continue
                ob.animation_data.action = act
                frame_start, frame_end = act.frame_range  # sic!
                add_anim(animations, animated,
                         fbx_animations_do(scene_data, (ob, act), frame_start, frame_end, True,
                                           objects={ob_obj}, force_keep=True))
                # Ugly! :/
                if pbones_matrices is not ...:
                    for pbo, mat in zip(ob.pose.bones, pbones_matrices):
                        pbo.matrix_basis = mat.copy()
                ob.animation_data.action = org_act
                restore_object(ob, ob_copy)

            if pbones_matrices is not ...:
                for pbo, mat in zip(ob.pose.bones, pbones_matrices):
                    pbo.matrix_basis = mat.copy()
            ob.animation_data.action = org_act

            bpy.data.objects.remove(ob_copy)

    # Global (containing everything) animstack, only if not exporting NLA strips and/or all actions.
    if not scene_data.settings.bake_anim_use_nla_strips and not scene_data.settings.bake_anim_use_all_actions:
        add_anim(animations, animated, fbx_animations_do(scene_data, None, scene.frame_start, scene.frame_end, False))

    # Be sure to update all matrices back to org state!
    scene.frame_set(scene.frame_current, 0.0)

    return animations, animated, frame_start, frame_end


