def fbx_skeleton_from_armature(scene, settings, arm_obj, objects, data_meshes,
                               data_bones, data_deformers_skin, data_empties, arm_parents):
    """
    Create skeleton from armature/bones (NodeAttribute/LimbNode and Model/LimbNode), and for each deformed mesh,
    create Pose/BindPose(with sub PoseNode) and Deformer/Skin(with Deformer/SubDeformer/Cluster).
    Also supports "parent to bone" (simple parent to Model/LimbNode).
    arm_parents is a set of tuples (armature, object) for all successful armature bindings.
    """
    # We need some data for our armature 'object' too!!!
    data_empties[arm_obj] = get_blender_empty_key(arm_obj.bdata)

    arm_data = arm_obj.bdata.data
    bones = OrderedDict()
    for bo in arm_obj.bones:
        if settings.use_armature_deform_only:
            if bo.bdata.use_deform:
                bones[bo] = True
                bo_par = bo.parent
                while bo_par.is_bone:
                    bones[bo_par] = True
                    bo_par = bo_par.parent
            elif bo not in bones:  # Do not override if already set in the loop above!
                bones[bo] = False
        else:
            bones[bo] = True

    bones = OrderedDict((bo, None) for bo, use in bones.items() if use)

    if not bones:
        return

    data_bones.update((bo, get_blender_bone_key(arm_obj.bdata, bo.bdata)) for bo in bones)

    for ob_obj in objects:
        if not ob_obj.is_deformed_by_armature(arm_obj):
            continue

        # Always handled by an Armature modifier...
        found = False
        for mod in ob_obj.bdata.modifiers:
            if mod.type not in {'ARMATURE'} or not mod.object:
                continue
            # We only support vertex groups binding method, not bone envelopes one!
            if mod.object in {arm_obj.bdata, arm_obj.bdata.proxy} and mod.use_vertex_groups:
                found = True
                break

        if not found:
            continue

        # Now we have a mesh using this armature.
        # Note: bindpose have no relations at all (no connections), so no need for any preprocess for them.
        # Create skin & clusters relations (note skins are connected to geometry, *not* model!).
        _key, me, _free = data_meshes[ob_obj]
        clusters = OrderedDict((bo, get_blender_bone_cluster_key(arm_obj.bdata, me, bo.bdata)) for bo in bones)
        data_deformers_skin.setdefault(arm_obj, OrderedDict())[me] = (get_blender_armature_skin_key(arm_obj.bdata, me),
                                                                      ob_obj, clusters)

        # We don't want a regular parent relationship for those in FBX...
        arm_parents.add((arm_obj, ob_obj))
        # Needed to handle matrices/spaces (since we do not parent them to 'armature' in FBX :/ ).
        ob_obj.parented_to_armature = True

    objects.update(bones)


