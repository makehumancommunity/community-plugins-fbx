def fbx_template_def_animstack(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Description", ("", "p_string", False)),
        (b"LocalStart", (0, "p_timestamp", False)),
        (b"LocalStop", (0, "p_timestamp", False)),
        (b"ReferenceStart", (0, "p_timestamp", False)),
        (b"ReferenceStop", (0, "p_timestamp", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"AnimationStack", b"FbxAnimStack", props, nbr_users, [False])


