def fbx_template_def_video(scene, settings, override_defaults=None, nbr_users=0):
    # WIP...
    props = OrderedDict((
        # All pictures.
        (b"Width", (0, "p_integer", False)),
        (b"Height", (0, "p_integer", False)),
        (b"Path", ("", "p_string_url", False)),
        (b"AccessMode", (0, "p_enum", False)),  # Disk (0=Disk, 1=Mem, 2=DiskAsync).
        # All videos.
        (b"StartFrame", (0, "p_integer", False)),
        (b"StopFrame", (0, "p_integer", False)),
        (b"Offset", (0, "p_timestamp", False)),
        (b"PlaySpeed", (0.0, "p_double", False)),
        (b"FreeRunning", (False, "p_bool", False)),
        (b"Loop", (False, "p_bool", False)),
        (b"InterlaceMode", (0, "p_enum", False)),  # None, i.e. progressive.
        # Image sequences.
        (b"ImageSequence", (False, "p_bool", False)),
        (b"ImageSequenceOffset", (0, "p_integer", False)),
        (b"FrameRate", (0.0, "p_double", False)),
        (b"LastFrame", (0, "p_integer", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Video", b"FbxVideo", props, nbr_users, [False])


