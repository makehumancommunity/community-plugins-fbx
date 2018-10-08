def fbx_data_bindpose_element(objectsParent, key, id, count):
    """
    Helper, since bindpose are used by both meshes shape keys and armature bones...
    """
    # We assume bind pose for our bones are their "Editmode" pose...
    # All matrices are expected in global (world) space.
    fbx_pose = elem_data_single_int64(objectsParent, b"Pose", id)
    fbx_pose.add_string(fbx_name_class(key.encode()))
    fbx_pose.add_string(b"BindPose")

    elem_data_single_string(fbx_pose, b"Type", b"BindPose")
    elem_data_single_int32(fbx_pose, b"Version", FBX_POSE_BIND_VERSION)
    elem_data_single_int32(fbx_pose, b"NbPoseNodes", count)

    return fbx_pose

