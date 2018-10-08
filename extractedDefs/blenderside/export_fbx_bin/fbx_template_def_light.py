def fbx_template_def_light(scene, settings, override_defaults=None, nbr_users=0):
    gscale = settings.global_scale
    props = OrderedDict((
        (b"LightType", (0, "p_enum", False)),  # Point light.
        (b"CastLight", (True, "p_bool", False)),
        (b"Color", ((1.0, 1.0, 1.0), "p_color", True)),
        (b"Intensity", (100.0, "p_number", True)),  # Times 100 compared to Blender values...
        (b"DecayType", (2, "p_enum", False)),  # Quadratic.
        (b"DecayStart", (30.0 * gscale, "p_double", False)),
        (b"CastShadows", (True, "p_bool", False)),
        (b"ShadowColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"AreaLightShape", (0, "p_enum", False)),  # Rectangle.
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"NodeAttribute", b"FbxLight", props, nbr_users, [False])


