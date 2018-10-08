def fbx_generate_leaf_bones(settings, data_bones):
    # find which bons have no children
    child_count = {bo: 0 for bo in data_bones.keys()}
    for bo in data_bones.keys():
        if bo.parent and bo.parent.is_bone:
            child_count[bo.parent] += 1

    bone_radius_scale = settings.global_scale * 33.0

    # generate bone data
    leaf_parents = [bo for bo, count in child_count.items() if count == 0]
    leaf_bones = []
    for parent in leaf_parents:
        node_name = parent.name + "_end"
        parent_uuid = parent.fbx_uuid
        parent_key = parent.key
        node_uuid = get_fbx_uuid_from_key(parent_key + "_end_node")
        attr_uuid = get_fbx_uuid_from_key(parent_key + "_end_nodeattr")

        hide = parent.hide
        size = parent.bdata.head_radius * bone_radius_scale
        bone_length = (parent.bdata.tail_local - parent.bdata.head_local).length
        matrix = Matrix.Translation((0, bone_length, 0))
        if settings.bone_correction_matrix_inv:
            matrix = settings.bone_correction_matrix_inv * matrix
        if settings.bone_correction_matrix:
            matrix = matrix * settings.bone_correction_matrix
        leaf_bones.append((node_name, parent_uuid, node_uuid, attr_uuid, matrix, hide, size))

    return leaf_bones


