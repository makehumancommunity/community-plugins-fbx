def fbx_template_def_null(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Color", ((0.8, 0.8, 0.8), "p_color_rgb", False)),
        (b"Size", (100.0, "p_double", False)),
        (b"Look", (1, "p_enum", False)),  # Cross (0 is None, i.e. invisible?).
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"NodeAttribute", b"FbxNull", props, nbr_users, [False])


