def fbx_template_def_texture_file(scene, settings, override_defaults=None, nbr_users=0):
    # WIP...
    # XXX Not sure about all names!
    props = OrderedDict((
        (b"TextureTypeUse", (0, "p_enum", False)),  # Standard.
        (b"AlphaSource", (2, "p_enum", False)),  # Black (i.e. texture's alpha), XXX name guessed!.
        (b"Texture alpha", (1.0, "p_double", False)),
        (b"PremultiplyAlpha", (True, "p_bool", False)),
        (b"CurrentTextureBlendMode", (1, "p_enum", False)),  # Additive...
        (b"CurrentMappingType", (0, "p_enum", False)),  # UV.
        (b"UVSet", ("default", "p_string", False)),  # UVMap name.
        (b"WrapModeU", (0, "p_enum", False)),  # Repeat.
        (b"WrapModeV", (0, "p_enum", False)),  # Repeat.
        (b"UVSwap", (False, "p_bool", False)),
        (b"Translation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Rotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Scaling", ((1.0, 1.0, 1.0), "p_vector_3d", False)),
        (b"TextureRotationPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TextureScalingPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        # Not sure about those two...
        (b"UseMaterial", (False, "p_bool", False)),
        (b"UseMipMap", (False, "p_bool", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Texture", b"FbxFileTexture", props, nbr_users, [False])


