def fbx_template_def_material(scene, settings, override_defaults=None, nbr_users=0):
    # WIP...
    props = OrderedDict((
        (b"ShadingModel", ("Phong", "p_string", False)),
        (b"MultiLayer", (False, "p_bool", False)),
        # Lambert-specific.
        (b"EmissiveColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"EmissiveFactor", (1.0, "p_number", True)),
        (b"AmbientColor", ((0.2, 0.2, 0.2), "p_color", True)),
        (b"AmbientFactor", (1.0, "p_number", True)),
        (b"DiffuseColor", ((0.8, 0.8, 0.8), "p_color", True)),
        (b"DiffuseFactor", (1.0, "p_number", True)),
        (b"TransparentColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"TransparencyFactor", (0.0, "p_number", True)),
        (b"Opacity", (1.0, "p_number", True)),
        (b"NormalMap", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Bump", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"BumpFactor", (1.0, "p_double", False)),
        (b"DisplacementColor", ((0.0, 0.0, 0.0), "p_color_rgb", False)),
        (b"DisplacementFactor", (1.0, "p_double", False)),
        (b"VectorDisplacementColor", ((0.0, 0.0, 0.0), "p_color_rgb", False)),
        (b"VectorDisplacementFactor", (1.0, "p_double", False)),
        # Phong-specific.
        (b"SpecularColor", ((0.2, 0.2, 0.2), "p_color", True)),
        (b"SpecularFactor", (1.0, "p_number", True)),
        # Not sure about the name, importer uses this (but ShininessExponent for tex prop name!)
        # And in fbx exported by sdk, you have one in template, the other in actual material!!! :/
        # For now, using both.
        (b"Shininess", (20.0, "p_number", True)),
        (b"ShininessExponent", (20.0, "p_number", True)),
        (b"ReflectionColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"ReflectionFactor", (1.0, "p_number", True)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Material", b"FbxSurfacePhong", props, nbr_users, [False])


