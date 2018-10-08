def fbx_template_def_geometry(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Color", ((0.8, 0.8, 0.8), "p_color_rgb", False)),
        (b"BBoxMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"BBoxMax", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Primary Visibility", (True, "p_bool", False)),
        (b"Casts Shadows", (True, "p_bool", False)),
        (b"Receive Shadows", (True, "p_bool", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Geometry", b"FbxMesh", props, nbr_users, [False])


