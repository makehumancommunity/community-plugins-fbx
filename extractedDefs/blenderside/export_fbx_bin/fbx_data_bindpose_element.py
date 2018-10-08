def fbx_data_bindpose_element(root, me_obj, me, scene_data, arm_obj=None, mat_world_arm=None, bones=[]):
    """
    Helper, since bindpose are used by both meshes shape keys and armature bones...
    """
    if arm_obj is None:
        arm_obj = me_obj
    # We assume bind pose for our bones are their "Editmode" pose...
    # All matrices are expected in global (world) space.
    bindpose_key = get_blender_bindpose_key(arm_obj.bdata, me)
    fbx_pose = elem_data_single_int64(root, b"Pose", get_fbx_uuid_from_key(bindpose_key))
    fbx_pose.add_string(fbx_name_class(me.name.encode(), b"Pose"))
    fbx_pose.add_string(b"BindPose")

    elem_data_single_string(fbx_pose, b"Type", b"BindPose")
    elem_data_single_int32(fbx_pose, b"Version", FBX_POSE_BIND_VERSION)
    elem_data_single_int32(fbx_pose, b"NbPoseNodes", 1 + (1 if (arm_obj != me_obj) else 0) + len(bones))

    # First node is mesh/object.
    mat_world_obj = me_obj.fbx_object_matrix(scene_data, global_space=True)
    fbx_posenode = elem_empty(fbx_pose, b"PoseNode")
    elem_data_single_int64(fbx_posenode, b"Node", me_obj.fbx_uuid)
    elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(mat_world_obj))
    # Second node is armature object itself.
    if arm_obj != me_obj:
        fbx_posenode = elem_empty(fbx_pose, b"PoseNode")
        elem_data_single_int64(fbx_posenode, b"Node", arm_obj.fbx_uuid)
        elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(mat_world_arm))
    # And all bones of armature!
    mat_world_bones = {}
    for bo_obj in bones:
        bomat = bo_obj.fbx_object_matrix(scene_data, rest=True, global_space=True)
        mat_world_bones[bo_obj] = bomat
        fbx_posenode = elem_empty(fbx_pose, b"PoseNode")
        elem_data_single_int64(fbx_posenode, b"Node", bo_obj.fbx_uuid)
        elem_data_single_float64_array(fbx_posenode, b"Matrix", matrix4_to_array(bomat))

    return mat_world_obj, mat_world_bones


