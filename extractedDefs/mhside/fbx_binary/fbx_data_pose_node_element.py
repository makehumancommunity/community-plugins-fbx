def fbx_data_pose_node_element(bindposeParent, key, id, bindmat):
    fbx_posenode = elem_empty(bindposeParent, b"PoseNode")
    elem_data_single_int64(fbx_posenode, b"Node", id)
    elem_data_single_float64_array(fbx_posenode, b"Matrix", bindmat.ravel(order='C'))  # Use column-major order

