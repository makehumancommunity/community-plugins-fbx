def fbx_data_mesh_elements(root, me_obj, scene_data, done_meshes):
    """
    Write the Mesh (Geometry) data block.
    """
    # Ugly helper... :/
    def _infinite_gen(val):
        while 1:
            yield val

    me_key, me, _free = scene_data.data_meshes[me_obj]

    # In case of multiple instances of same mesh, only write it once!
    if me_key in done_meshes:
        return

    # No gscale/gmat here, all data are supposed to be in object space.
    smooth_type = scene_data.settings.mesh_smooth_type
    write_normals = True  # smooth_type in {'OFF'}

    do_bake_space_transform = me_obj.use_bake_space_transform(scene_data)

    # Vertices are in object space, but we are post-multiplying all transforms with the inverse of the
    # global matrix, so we need to apply the global matrix to the vertices to get the correct result.
    geom_mat_co = scene_data.settings.global_matrix if do_bake_space_transform else None
    # We need to apply the inverse transpose of the global matrix when transforming normals.
    geom_mat_no = Matrix(scene_data.settings.global_matrix_inv_transposed) if do_bake_space_transform else None
    if geom_mat_no is not None:
        # Remove translation & scaling!
        geom_mat_no.translation = Vector()
        geom_mat_no.normalize()

    geom = elem_data_single_int64(root, b"Geometry", get_fbx_uuid_from_key(me_key))
    geom.add_string(fbx_name_class(me.name.encode(), b"Geometry"))
    geom.add_string(b"Mesh")

    tmpl = elem_props_template_init(scene_data.templates, b"Geometry")
    props = elem_properties(geom)

    # Custom properties.
    if scene_data.settings.use_custom_props:
        fbx_data_element_custom_properties(props, me)

    elem_data_single_int32(geom, b"GeometryVersion", FBX_GEOMETRY_VERSION)

    # Vertex cos.
    t_co = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.vertices) * 3
    me.vertices.foreach_get("co", t_co)
    elem_data_single_float64_array(geom, b"Vertices", chain(*vcos_transformed_gen(t_co, geom_mat_co)))
    del t_co

    # Polygon indices.
    #
    # We do loose edges as two-vertices faces, if enabled...
    #
    # Note we have to process Edges in the same time, as they are based on poly's loops...
    loop_nbr = len(me.loops)
    t_pvi = array.array(data_types.ARRAY_INT32, (0,)) * loop_nbr
    t_ls = [None] * len(me.polygons)

    me.loops.foreach_get("vertex_index", t_pvi)
    me.polygons.foreach_get("loop_start", t_ls)

    # Add "fake" faces for loose edges.
    if scene_data.settings.use_mesh_edges:
        t_le = tuple(e.vertices for e in me.edges if e.is_loose)
        t_pvi.extend(chain(*t_le))
        t_ls.extend(range(loop_nbr, loop_nbr + len(t_le), 2))
        del t_le

    # Edges...
    # Note: Edges are represented as a loop here: each edge uses a single index, which refers to the polygon array.
    #       The edge is made by the vertex indexed py this polygon's point and the next one on the same polygon.
    #       Advantage: Only one index per edge.
    #       Drawback: Only polygon's edges can be represented (that's why we have to add fake two-verts polygons
    #                 for loose edges).
    #       We also have to store a mapping from real edges to their indices in this array, for edge-mapped data
    #       (like e.g. crease).
    t_eli = array.array(data_types.ARRAY_INT32)
    edges_map = {}
    edges_nbr = 0
    if t_ls and t_pvi:
        t_ls = set(t_ls)
        todo_edges = [None] * len(me.edges) * 2
        # Sigh, cannot access edge.key through foreach_get... :/
        me.edges.foreach_get("vertices", todo_edges)
        todo_edges = set((v1, v2) if v1 < v2 else (v2, v1) for v1, v2 in zip(*(iter(todo_edges),) * 2))

        li = 0
        vi = vi_start = t_pvi[0]
        for li_next, vi_next in enumerate(t_pvi[1:] + t_pvi[:1], start=1):
            if li_next in t_ls:  # End of a poly's loop.
                vi2 = vi_start
                vi_start = vi_next
            else:
                vi2 = vi_next

            e_key = (vi, vi2) if vi < vi2 else (vi2, vi)
            if e_key in todo_edges:
                t_eli.append(li)
                todo_edges.remove(e_key)
                edges_map[e_key] = edges_nbr
                edges_nbr += 1

            vi = vi_next
            li = li_next
    # End of edges!

    # We have to ^-1 last index of each loop.
    for ls in t_ls:
        t_pvi[ls - 1] ^= -1

    # And finally we can write data!
    elem_data_single_int32_array(geom, b"PolygonVertexIndex", t_pvi)
    elem_data_single_int32_array(geom, b"Edges", t_eli)
    del t_pvi
    del t_ls
    del t_eli

    # And now, layers!

    # Smoothing.
    if smooth_type in {'FACE', 'EDGE'}:
        t_ps = None
        _map = b""
        if smooth_type == 'FACE':
            t_ps = array.array(data_types.ARRAY_INT32, (0,)) * len(me.polygons)
            me.polygons.foreach_get("use_smooth", t_ps)
            _map = b"ByPolygon"
        else:  # EDGE
            # Write Edge Smoothing.
            # Note edge is sharp also if it's used by more than two faces, or one of its faces is flat.
            t_ps = array.array(data_types.ARRAY_INT32, (0,)) * edges_nbr
            sharp_edges = set()
            temp_sharp_edges = {}
            for p in me.polygons:
                if not p.use_smooth:
                    sharp_edges.update(p.edge_keys)
                    continue
                for k in p.edge_keys:
                    if temp_sharp_edges.setdefault(k, 0) > 1:
                        sharp_edges.add(k)
                    else:
                        temp_sharp_edges[k] += 1
            del temp_sharp_edges
            for e in me.edges:
                if e.key not in edges_map:
                    continue  # Only loose edges, in theory!
                t_ps[edges_map[e.key]] = not (e.use_edge_sharp or (e.key in sharp_edges))
            _map = b"ByEdge"
        lay_smooth = elem_data_single_int32(geom, b"LayerElementSmoothing", 0)
        elem_data_single_int32(lay_smooth, b"Version", FBX_GEOMETRY_SMOOTHING_VERSION)
        elem_data_single_string(lay_smooth, b"Name", b"")
        elem_data_single_string(lay_smooth, b"MappingInformationType", _map)
        elem_data_single_string(lay_smooth, b"ReferenceInformationType", b"Direct")
        elem_data_single_int32_array(lay_smooth, b"Smoothing", t_ps)  # Sight, int32 for bool...
        del t_ps

    # TODO: Edge crease (LayerElementCrease).

    # And we are done with edges!
    del edges_map

    # Loop normals.
    tspacenumber = 0
    if write_normals:
        # NOTE: this is not supported by importer currently.
        # XXX Official docs says normals should use IndexToDirect,
        #     but this does not seem well supported by apps currently...
        me.calc_normals_split()

        t_ln = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops) * 3
        me.loops.foreach_get("normal", t_ln)
        t_ln = nors_transformed_gen(t_ln, geom_mat_no)
        if 0:
            t_ln = tuple(t_ln)  # No choice... :/

            lay_nor = elem_data_single_int32(geom, b"LayerElementNormal", 0)
            elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_NORMAL_VERSION)
            elem_data_single_string(lay_nor, b"Name", b"")
            elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_nor, b"ReferenceInformationType", b"IndexToDirect")

            ln2idx = tuple(set(t_ln))
            elem_data_single_float64_array(lay_nor, b"Normals", chain(*ln2idx))
            # Normal weights, no idea what it is.
            # t_lnw = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(ln2idx)
            # elem_data_single_float64_array(lay_nor, b"NormalsW", t_lnw)

            ln2idx = {nor: idx for idx, nor in enumerate(ln2idx)}
            elem_data_single_int32_array(lay_nor, b"NormalsIndex", (ln2idx[n] for n in t_ln))

            del ln2idx
            # del t_lnw
        else:
            lay_nor = elem_data_single_int32(geom, b"LayerElementNormal", 0)
            elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_NORMAL_VERSION)
            elem_data_single_string(lay_nor, b"Name", b"")
            elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_nor, b"ReferenceInformationType", b"Direct")
            elem_data_single_float64_array(lay_nor, b"Normals", chain(*t_ln))
            # Normal weights, no idea what it is.
            # t_ln = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops)
            # elem_data_single_float64_array(lay_nor, b"NormalsW", t_ln)
        del t_ln

        # tspace
        if scene_data.settings.use_tspace:
            tspacenumber = len(me.uv_layers)
            if tspacenumber:
                t_ln = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops) * 3
                # t_lnw = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops)
                for idx, uvlayer in enumerate(me.uv_layers):
                    name = uvlayer.name
                    me.calc_tangents(name)
                    # Loop bitangents (aka binormals).
                    # NOTE: this is not supported by importer currently.
                    me.loops.foreach_get("bitangent", t_ln)
                    lay_nor = elem_data_single_int32(geom, b"LayerElementBinormal", idx)
                    elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_BINORMAL_VERSION)
                    elem_data_single_string_unicode(lay_nor, b"Name", name)
                    elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
                    elem_data_single_string(lay_nor, b"ReferenceInformationType", b"Direct")
                    elem_data_single_float64_array(lay_nor, b"Binormals",
                                                   chain(*nors_transformed_gen(t_ln, geom_mat_no)))
                    # Binormal weights, no idea what it is.
                    # elem_data_single_float64_array(lay_nor, b"BinormalsW", t_lnw)

                    # Loop tangents.
                    # NOTE: this is not supported by importer currently.
                    me.loops.foreach_get("tangent", t_ln)
                    lay_nor = elem_data_single_int32(geom, b"LayerElementTangent", idx)
                    elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_TANGENT_VERSION)
                    elem_data_single_string_unicode(lay_nor, b"Name", name)
                    elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
                    elem_data_single_string(lay_nor, b"ReferenceInformationType", b"Direct")
                    elem_data_single_float64_array(lay_nor, b"Tangents",
                                                   chain(*nors_transformed_gen(t_ln, geom_mat_no)))
                    # Tangent weights, no idea what it is.
                    # elem_data_single_float64_array(lay_nor, b"TangentsW", t_lnw)

                del t_ln
                # del t_lnw
                me.free_tangents()

        me.free_normals_split()

    # Write VertexColor Layers.
    vcolnumber = len(me.vertex_colors)
    if vcolnumber:
        def _coltuples_gen(raw_cols):
            return zip(*(iter(raw_cols),) * 3 + (_infinite_gen(1.0),))  # We need a fake alpha...

        t_lc = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops) * 3
        for colindex, collayer in enumerate(me.vertex_colors):
            collayer.data.foreach_get("color", t_lc)
            lay_vcol = elem_data_single_int32(geom, b"LayerElementColor", colindex)
            elem_data_single_int32(lay_vcol, b"Version", FBX_GEOMETRY_VCOLOR_VERSION)
            elem_data_single_string_unicode(lay_vcol, b"Name", collayer.name)
            elem_data_single_string(lay_vcol, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_vcol, b"ReferenceInformationType", b"IndexToDirect")

            col2idx = tuple(set(_coltuples_gen(t_lc)))
            elem_data_single_float64_array(lay_vcol, b"Colors", chain(*col2idx))  # Flatten again...

            col2idx = {col: idx for idx, col in enumerate(col2idx)}
            elem_data_single_int32_array(lay_vcol, b"ColorIndex", (col2idx[c] for c in _coltuples_gen(t_lc)))
            del col2idx
        del t_lc
        del _coltuples_gen

    # Write UV layers.
    # Note: LayerElementTexture is deprecated since FBX 2011 - luckily!
    #       Textures are now only related to materials, in FBX!
    uvnumber = len(me.uv_layers)
    if uvnumber:
        def _uvtuples_gen(raw_uvs):
            return zip(*(iter(raw_uvs),) * 2)

        t_luv = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops) * 2
        for uvindex, uvlayer in enumerate(me.uv_layers):
            uvlayer.data.foreach_get("uv", t_luv)
            lay_uv = elem_data_single_int32(geom, b"LayerElementUV", uvindex)
            elem_data_single_int32(lay_uv, b"Version", FBX_GEOMETRY_UV_VERSION)
            elem_data_single_string_unicode(lay_uv, b"Name", uvlayer.name)
            elem_data_single_string(lay_uv, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_uv, b"ReferenceInformationType", b"IndexToDirect")

            uv2idx = tuple(set(_uvtuples_gen(t_luv)))
            elem_data_single_float64_array(lay_uv, b"UV", chain(*uv2idx))  # Flatten again...

            uv2idx = {uv: idx for idx, uv in enumerate(uv2idx)}
            elem_data_single_int32_array(lay_uv, b"UVIndex", (uv2idx[uv] for uv in _uvtuples_gen(t_luv)))
            del uv2idx
        del t_luv
        del _uvtuples_gen

    # Face's materials.
    me_fbxmats_idx = scene_data.mesh_mat_indices.get(me)
    if me_fbxmats_idx is not None:
        me_blmats = me.materials
        if me_fbxmats_idx and me_blmats:
            lay_mat = elem_data_single_int32(geom, b"LayerElementMaterial", 0)
            elem_data_single_int32(lay_mat, b"Version", FBX_GEOMETRY_MATERIAL_VERSION)
            elem_data_single_string(lay_mat, b"Name", b"")
            nbr_mats = len(me_fbxmats_idx)
            if nbr_mats > 1:
                t_pm = array.array(data_types.ARRAY_INT32, (0,)) * len(me.polygons)
                me.polygons.foreach_get("material_index", t_pm)

                # We have to validate mat indices, and map them to FBX indices.
                # Note a mat might not be in me_fbxmats_idx (e.g. node mats are ignored).
                blmats_to_fbxmats_idxs = [me_fbxmats_idx[m] for m in me_blmats if m in me_fbxmats_idx]
                mat_idx_limit = len(blmats_to_fbxmats_idxs)
                def_mat = blmats_to_fbxmats_idxs[0]
                _gen = (blmats_to_fbxmats_idxs[m] if m < mat_idx_limit else def_mat for m in t_pm)
                t_pm = array.array(data_types.ARRAY_INT32, _gen)

                elem_data_single_string(lay_mat, b"MappingInformationType", b"ByPolygon")
                # XXX Logically, should be "Direct" reference type, since we do not have any index array, and have one
                #     value per polygon...
                #     But looks like FBX expects it to be IndexToDirect here (maybe because materials are already
                #     indices??? *sigh*).
                elem_data_single_string(lay_mat, b"ReferenceInformationType", b"IndexToDirect")
                elem_data_single_int32_array(lay_mat, b"Materials", t_pm)
                del t_pm
            else:
                elem_data_single_string(lay_mat, b"MappingInformationType", b"AllSame")
                elem_data_single_string(lay_mat, b"ReferenceInformationType", b"IndexToDirect")
                elem_data_single_int32_array(lay_mat, b"Materials", [0])

    # And the "layer TOC"...

    layer = elem_data_single_int32(geom, b"Layer", 0)
    elem_data_single_int32(layer, b"Version", FBX_GEOMETRY_LAYER_VERSION)
    if write_normals:
        lay_nor = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_nor, b"Type", b"LayerElementNormal")
        elem_data_single_int32(lay_nor, b"TypedIndex", 0)
    if tspacenumber:
        lay_binor = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_binor, b"Type", b"LayerElementBinormal")
        elem_data_single_int32(lay_binor, b"TypedIndex", 0)
        lay_tan = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_tan, b"Type", b"LayerElementTangent")
        elem_data_single_int32(lay_tan, b"TypedIndex", 0)
    if smooth_type in {'FACE', 'EDGE'}:
        lay_smooth = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_smooth, b"Type", b"LayerElementSmoothing")
        elem_data_single_int32(lay_smooth, b"TypedIndex", 0)
    if vcolnumber:
        lay_vcol = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_vcol, b"Type", b"LayerElementColor")
        elem_data_single_int32(lay_vcol, b"TypedIndex", 0)
    if uvnumber:
        lay_uv = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_uv, b"Type", b"LayerElementUV")
        elem_data_single_int32(lay_uv, b"TypedIndex", 0)
    if me_fbxmats_idx is not None:
        lay_mat = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_mat, b"Type", b"LayerElementMaterial")
        elem_data_single_int32(lay_mat, b"TypedIndex", 0)

    # Add other uv and/or vcol layers...
    for vcolidx, uvidx, tspaceidx in zip_longest(range(1, vcolnumber), range(1, uvnumber), range(1, tspacenumber),
                                                 fillvalue=0):
        layer = elem_data_single_int32(geom, b"Layer", max(vcolidx, uvidx))
        elem_data_single_int32(layer, b"Version", FBX_GEOMETRY_LAYER_VERSION)
        if vcolidx:
            lay_vcol = elem_empty(layer, b"LayerElement")
            elem_data_single_string(lay_vcol, b"Type", b"LayerElementColor")
            elem_data_single_int32(lay_vcol, b"TypedIndex", vcolidx)
        if uvidx:
            lay_uv = elem_empty(layer, b"LayerElement")
            elem_data_single_string(lay_uv, b"Type", b"LayerElementUV")
            elem_data_single_int32(lay_uv, b"TypedIndex", uvidx)
        if tspaceidx:
            lay_binor = elem_empty(layer, b"LayerElement")
            elem_data_single_string(lay_binor, b"Type", b"LayerElementBinormal")
            elem_data_single_int32(lay_binor, b"TypedIndex", tspaceidx)
            lay_tan = elem_empty(layer, b"LayerElement")
            elem_data_single_string(lay_tan, b"Type", b"LayerElementTangent")
            elem_data_single_int32(lay_tan, b"TypedIndex", tspaceidx)

    # Shape keys...
    fbx_data_mesh_shapes_elements(root, me_obj, me, scene_data, tmpl, props)

    elem_props_template_finalize(tmpl, props)
    done_meshes.add(me_key)


