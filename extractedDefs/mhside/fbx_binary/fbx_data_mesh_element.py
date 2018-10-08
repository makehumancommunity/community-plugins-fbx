def fbx_data_mesh_element(objectsParent, key, id, properties, coord, fvert, vnorm, texco, fuv):
    geom = elem_data_single_int64(objectsParent, b"Geometry", id)  #get_fbx_uuid_from_key(key))
    geom.add_string(fbx_name_class(key.encode()))
    geom.add_string(b"Mesh")

    name = key.split('::')[1]

    props = elem_properties(geom)

    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)
        #fbx_data_element_custom_properties(props, me)


    # Vertex cos.
    t_co = array.array(data_types.ARRAY_FLOAT64, coord.reshape(-1))
    elem_data_single_float64_array(geom, b"Vertices", t_co)
    del t_co

    # Polygon indices.
    # Bitwise negate last index to mark end of polygon loop
    fvert_ = fvert.copy()
    if fvert.shape[1] == 3:
        #fvert_[:,2] = -1 - fvert_[:,2]
        fvert_[:,2] = ~fvert_[:,2]
    else:
        fvert_[:,3] = ~fvert_[:,3]
    import numpy as np
    t_pvi = array.array(data_types.ARRAY_INT32, fvert_.astype(np.int32).reshape(-1))
    elem_data_single_int32_array(geom, b"PolygonVertexIndex", t_pvi)


    #elem_data_single_int32_array(geom, b"Edges", t_eli)
    del t_pvi

    elem_data_single_int32(geom, b"GeometryVersion", 124)

    # Layers

    # Normals
    t_ln = array.array(data_types.ARRAY_FLOAT64, vnorm.reshape(-1))

    lay_nor = elem_data_single_int32(geom, b"LayerElementNormal", 0)
    elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_NORMAL_VERSION)
    elem_data_single_string(lay_nor, b"Name", (name+"_Normal").encode())
    elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
    elem_data_single_string(lay_nor, b"ReferenceInformationType", b"IndexToDirect")

    elem_data_single_float64_array(lay_nor, b"Normals", t_ln)

    elem_data_single_int32_array(lay_nor, b"NormalsIndex", fvert.reshape(-1))
    del t_ln

    # TODO export tangents
    '''
    # tspace
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

        # del t_lnw
    '''

    # TODO export vertex colors
    '''
    # VertexColor Layers.
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
    '''

    # UV layers.
    # Note: LayerElementTexture is deprecated since FBX 2011 - luckily!
    #       Textures are now only related to materials, in FBX!
    t_uv = array.array(data_types.ARRAY_FLOAT64, texco.reshape(-1))
    t_fuv = array.array(data_types.ARRAY_INT32, fuv.reshape(-1))
    uvindex = 0
    lay_uv = elem_data_single_int32(geom, b"LayerElementUV", uvindex)
    elem_data_single_int32(lay_uv, b"Version", FBX_GEOMETRY_UV_VERSION)
    elem_data_single_string_unicode(lay_uv, b"Name", (name+"_UV").encode())
    elem_data_single_string(lay_uv, b"MappingInformationType", b"ByPolygonVertex")
    elem_data_single_string(lay_uv, b"ReferenceInformationType", b"IndexToDirect")

    # TODO verify whether this crashes FBX converter as well (and needs a hack like fbx_mesh.writeUvs2)
    elem_data_single_float64_array(lay_uv, b"UV", t_uv)
    elem_data_single_int32_array(lay_uv, b"UVIndex", t_fuv)

    del t_fuv
    del t_uv

    # Face's materials.
    lay_mat = elem_data_single_int32(geom, b"LayerElementMaterial", 0)
    elem_data_single_int32(lay_mat, b"Version", FBX_GEOMETRY_MATERIAL_VERSION)
    elem_data_single_string(lay_mat, b"Name", (name+"_Material").encode())

    elem_data_single_string(lay_mat, b"MappingInformationType", b"AllSame")
    elem_data_single_string(lay_mat, b"ReferenceInformationType", b"IndexToDirect")
    elem_data_single_int32_array(lay_mat, b"Materials", [0])

    # Face's textures -perhaps obsolete.
    lay_tex = elem_data_single_int32(geom, b"LayerElementTexture", 0)
    elem_data_single_int32(lay_tex, b"Version", 101)
    elem_data_single_string(lay_tex, b"Name", (name+"_Texture").encode())

    elem_data_single_string(lay_tex, b"MappingInformationType", b"ByPolygonVertex")
    elem_data_single_string(lay_tex, b"ReferenceInformationType", b"IndexToDirect")
    elem_data_single_string(lay_tex, b"BlendMode", b"Translucent")

    # Layer TOC
    layer = elem_data_single_int32(geom, b"Layer", 0)
    elem_data_single_int32(layer, b"Version", FBX_GEOMETRY_LAYER_VERSION)

    lay_nor = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_nor, b"Type", b"LayerElementNormal")
    elem_data_single_int32(lay_nor, b"TypedIndex", 0)

    # TODO tangents
    '''
    lay_binor = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_binor, b"Type", b"LayerElementBinormal")
    elem_data_single_int32(lay_binor, b"TypedIndex", 0)
    lay_tan = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_tan, b"Type", b"LayerElementTangent")
    elem_data_single_int32(lay_tan, b"TypedIndex", 0)
    '''

    # TODO vertex colors
    '''
    if vcolnumber:
        lay_vcol = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_vcol, b"Type", b"LayerElementColor")
        elem_data_single_int32(lay_vcol, b"TypedIndex", 0)
    '''

    lay_uv = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_uv, b"Type", b"LayerElementUV")
    elem_data_single_int32(lay_uv, b"TypedIndex", 0)

    lay_mat = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_mat, b"Type", b"LayerElementMaterial")
    elem_data_single_int32(lay_mat, b"TypedIndex", 0)

    lay_tex = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_tex, b"Type", b"LayerElementTexture")
    elem_data_single_int32(lay_tex, b"TypedIndex", 0)

    # Shape keys
    #fbx_data_mesh_shapes_elements(root, me_obj, me, scene_data, tmpl, props)


