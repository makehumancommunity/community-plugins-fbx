def fbx_data_texture_file_elements(root, tex, scene_data):
    """
    Write the (file) Texture data block.
    """
    # XXX All this is very fuzzy to me currently...
    #     Textures do not seem to use properties as much as they could.
    #     For now assuming most logical and simple stuff.

    tex_key, _mats = scene_data.data_textures[tex]
    img = tex.texture.image
    fname_abs, fname_rel = _gen_vid_path(img, scene_data)

    fbx_tex = elem_data_single_int64(root, b"Texture", get_fbx_uuid_from_key(tex_key))
    fbx_tex.add_string(fbx_name_class(tex.name.encode(), b"Texture"))
    fbx_tex.add_string(b"")

    elem_data_single_string(fbx_tex, b"Type", b"TextureVideoClip")
    elem_data_single_int32(fbx_tex, b"Version", FBX_TEXTURE_VERSION)
    elem_data_single_string(fbx_tex, b"TextureName", fbx_name_class(tex.name.encode(), b"Texture"))
    elem_data_single_string(fbx_tex, b"Media", fbx_name_class(img.name.encode(), b"Video"))
    elem_data_single_string_unicode(fbx_tex, b"FileName", fname_abs)
    elem_data_single_string_unicode(fbx_tex, b"RelativeFilename", fname_rel)

    alpha_source = 0  # None
    if img.use_alpha:
        if tex.texture.use_calculate_alpha:
            alpha_source = 1  # RGBIntensity as alpha.
        else:
            alpha_source = 2  # Black, i.e. alpha channel.
    # BlendMode not useful for now, only affects layered textures afaics.
    mapping = 0  # UV.
    uvset = None
    if tex.texture_coords in {'ORCO'}:  # XXX Others?
        if tex.mapping in {'FLAT'}:
            mapping = 1  # Planar
        elif tex.mapping in {'CUBE'}:
            mapping = 4  # Box
        elif tex.mapping in {'TUBE'}:
            mapping = 3  # Cylindrical
        elif tex.mapping in {'SPHERE'}:
            mapping = 2  # Spherical
    elif tex.texture_coords in {'UV'}:
        mapping = 0  # UV
        # Yuck, UVs are linked by mere names it seems... :/
        uvset = tex.uv_layer
    wrap_mode = 1  # Clamp
    if tex.texture.extension in {'REPEAT'}:
        wrap_mode = 0  # Repeat

    tmpl = elem_props_template_init(scene_data.templates, b"TextureFile")
    props = elem_properties(fbx_tex)
    elem_props_template_set(tmpl, props, "p_enum", b"AlphaSource", alpha_source)
    elem_props_template_set(tmpl, props, "p_bool", b"PremultiplyAlpha",
                            img.alpha_mode in {'STRAIGHT'})  # Or is it PREMUL?
    elem_props_template_set(tmpl, props, "p_enum", b"CurrentMappingType", mapping)
    if uvset is not None:
        elem_props_template_set(tmpl, props, "p_string", b"UVSet", uvset)
    elem_props_template_set(tmpl, props, "p_enum", b"WrapModeU", wrap_mode)
    elem_props_template_set(tmpl, props, "p_enum", b"WrapModeV", wrap_mode)
    elem_props_template_set(tmpl, props, "p_vector_3d", b"Translation", tex.offset)
    elem_props_template_set(tmpl, props, "p_vector_3d", b"Scaling", tex.scale)
    # UseMaterial should always be ON imho.
    elem_props_template_set(tmpl, props, "p_bool", b"UseMaterial", True)
    elem_props_template_set(tmpl, props, "p_bool", b"UseMipMap", tex.texture.use_mipmap)
    elem_props_template_finalize(tmpl, props)

    # Custom properties.
    if scene_data.settings.use_custom_props:
        fbx_data_element_custom_properties(props, tex.texture)


