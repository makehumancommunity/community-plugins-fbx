def fbx_data_subdeformer(objectsParent, key, id, indices, weights, bindmat, bindinv):
    # Create the cluster.
    fbx_clstr = elem_data_single_int64(objectsParent, b"Deformer", id)
    fbx_clstr.add_string(fbx_name_class(key))
    fbx_clstr.add_string(b"Cluster")

    elem_data_single_int32(fbx_clstr, b"Version", FBX_DEFORMER_CLUSTER_VERSION)
    # No idea what that user data might be...
    fbx_userdata = elem_data_single_string(fbx_clstr, b"UserData", b"")
    fbx_userdata.add_string(b"")
    elem_data_single_int32_array(fbx_clstr, b"Indexes", indices)
    elem_data_single_float64_array(fbx_clstr, b"Weights", weights)
    # Transform, TransformLink and TransformAssociateModel matrices...
    # They seem to be doublons of BindPose ones??? Have armature (associatemodel) in addition, though.
    # WARNING! Even though official FBX API presents Transform in global space,
    #          **it is stored in bone space in FBX data!** See:
    #          http://area.autodesk.com/forum/autodesk-fbx/fbx-sdk/why-the-values-return-
    #                 by-fbxcluster-gettransformmatrix-x-not-same-with-the-value-in-ascii-fbx-file/
    elem_data_single_float64_array(fbx_clstr, b"Transform", bindmat.ravel(order='C'))
    elem_data_single_float64_array(fbx_clstr, b"TransformLink", bindinv.ravel(order='C'))
    #elem_data_single_float64_array(fbx_clstr, b"TransformAssociateModel", matrix4_to_array(mat_world_arm))

