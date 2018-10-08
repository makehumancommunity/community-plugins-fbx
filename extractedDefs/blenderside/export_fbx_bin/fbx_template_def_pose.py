def fbx_template_def_pose(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict()
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Pose", b"", props, nbr_users, [False])


