def fbx_template_def_animcurvenode(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (FBX_ANIM_PROPSGROUP_NAME.encode(), (None, "p_compound", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"AnimationCurveNode", b"FbxAnimCurveNode", props, nbr_users, [False])


