def fbx_template_def_animlayer(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Weight", (100.0, "p_number", True)),
        (b"Mute", (False, "p_bool", False)),
        (b"Solo", (False, "p_bool", False)),
        (b"Lock", (False, "p_bool", False)),
        (b"Color", ((0.8, 0.8, 0.8), "p_color_rgb", False)),
        (b"BlendMode", (0, "p_enum", False)),
        (b"RotationAccumulationMode", (0, "p_enum", False)),
        (b"ScaleAccumulationMode", (0, "p_enum", False)),
        (b"BlendModeBypass", (0, "p_ulonglong", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"AnimationLayer", b"FbxAnimLayer", props, nbr_users, [False])


