def fbx_data_mesh_shapes_elements(root, me_obj, me, scene_data, fbx_me_tmpl, fbx_me_props):
    """
    Write shape keys related data.
    """
    if me not in scene_data.data_deformers_shape:
        return

    write_normals = True  # scene_data.settings.mesh_smooth_type in {'OFF'}

    # First, write the geometry data itself (i.e. shapes).
    _me_key, shape_key, shapes = scene_data.data_deformers_shape[me]

    channels = []

    for shape, (channel_key, geom_key, shape_verts_co, shape_verts_idx) in shapes.items():
        # Use vgroups as weights, if defined.
        if shape.vertex_group and shape.vertex_group in me_obj.bdata.vertex_groups:
            shape_verts_weights = [0.0] * (len(shape_verts_co) // 3)
            vg_idx = me_obj.bdata.vertex_groups[shape.vertex_group].index
            for sk_idx, v_idx in enumerate(shape_verts_idx):
                for vg in me.vertices[v_idx].groups:
                    if vg.group == vg_idx:
                        shape_verts_weights[sk_idx] = vg.weight * 100.0
        else:
            shape_verts_weights = [100.0] * (len(shape_verts_co) // 3)
        channels.append((channel_key, shape, shape_verts_weights))

        geom = elem_data_single_int64(root, b"Geometry", get_fbx_uuid_from_key(geom_key))
        geom.add_string(fbx_name_class(shape.name.encode(), b"Geometry"))
        geom.add_string(b"Shape")

        tmpl = elem_props_template_init(scene_data.templates, b"Geometry")
        props = elem_properties(geom)
        elem_props_template_finalize(tmpl, props)

        elem_data_single_int32(geom, b"Version", FBX_GEOMETRY_SHAPE_VERSION)

        elem_data_single_int32_array(geom, b"Indexes", shape_verts_idx)
        elem_data_single_float64_array(geom, b"Vertices", shape_verts_co)
        if write_normals:
            elem_data_single_float64_array(geom, b"Normals", [0.0] * len(shape_verts_co))

    # Yiha! BindPose for shapekeys too! Dodecasigh...
    # XXX Not sure yet whether several bindposes on same mesh are allowed, or not... :/
    fbx_data_bindpose_element(root, me_obj, me, scene_data)

    # ...and now, the deformers stuff.
    fbx_shape = elem_data_single_int64(root, b"Deformer", get_fbx_uuid_from_key(shape_key))
    fbx_shape.add_string(fbx_name_class(me.name.encode(), b"Deformer"))
    fbx_shape.add_string(b"BlendShape")

    elem_data_single_int32(fbx_shape, b"Version", FBX_DEFORMER_SHAPE_VERSION)

    for channel_key, shape, shape_verts_weights in channels:
        fbx_channel = elem_data_single_int64(root, b"Deformer", get_fbx_uuid_from_key(channel_key))
        fbx_channel.add_string(fbx_name_class(shape.name.encode(), b"SubDeformer"))
        fbx_channel.add_string(b"BlendShapeChannel")

        elem_data_single_int32(fbx_channel, b"Version", FBX_DEFORMER_SHAPECHANNEL_VERSION)
        elem_data_single_float64(fbx_channel, b"DeformPercent", shape.value * 100.0)  # Percents...
        elem_data_single_float64_array(fbx_channel, b"FullWeights", shape_verts_weights)

        # *WHY* add this in linked mesh properties too? *cry*
        # No idea whether it’s percent here too, or more usual factor (assume percentage for now) :/
        elem_props_template_set(fbx_me_tmpl, fbx_me_props, "p_number", shape.name.encode(), shape.value * 100.0,
                                animatable=True)


