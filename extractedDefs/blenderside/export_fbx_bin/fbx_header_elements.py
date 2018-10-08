def fbx_header_elements(root, scene_data, time=None):
    """
    Write boiling code of FBX root.
    time is expected to be a datetime.datetime object, or None (using now() in this case).
    """
    app_vendor = "Blender Foundation"
    app_name = "Blender (stable FBX IO)"
    app_ver = bpy.app.version_string

    import addon_utils
    import sys
    addon_ver = addon_utils.module_bl_info(sys.modules[__package__])['version']

    # ##### Start of FBXHeaderExtension element.
    header_ext = elem_empty(root, b"FBXHeaderExtension")

    elem_data_single_int32(header_ext, b"FBXHeaderVersion", FBX_HEADER_VERSION)

    elem_data_single_int32(header_ext, b"FBXVersion", FBX_VERSION)

    # No encryption!
    elem_data_single_int32(header_ext, b"EncryptionType", 0)

    if time is None:
        time = datetime.datetime.now()
    elem = elem_empty(header_ext, b"CreationTimeStamp")
    elem_data_single_int32(elem, b"Version", 1000)
    elem_data_single_int32(elem, b"Year", time.year)
    elem_data_single_int32(elem, b"Month", time.month)
    elem_data_single_int32(elem, b"Day", time.day)
    elem_data_single_int32(elem, b"Hour", time.hour)
    elem_data_single_int32(elem, b"Minute", time.minute)
    elem_data_single_int32(elem, b"Second", time.second)
    elem_data_single_int32(elem, b"Millisecond", time.microsecond // 1000)

    elem_data_single_string_unicode(header_ext, b"Creator", "%s - %s - %d.%d.%d"
                                                % (app_name, app_ver, addon_ver[0], addon_ver[1], addon_ver[2]))

    # 'SceneInfo' seems mandatory to get a valid FBX file...
    # TODO use real values!
    # XXX Should we use scene.name.encode() here?
    scene_info = elem_data_single_string(header_ext, b"SceneInfo", fbx_name_class(b"GlobalInfo", b"SceneInfo"))
    scene_info.add_string(b"UserData")
    elem_data_single_string(scene_info, b"Type", b"UserData")
    elem_data_single_int32(scene_info, b"Version", FBX_SCENEINFO_VERSION)
    meta_data = elem_empty(scene_info, b"MetaData")
    elem_data_single_int32(meta_data, b"Version", FBX_SCENEINFO_VERSION)
    elem_data_single_string(meta_data, b"Title", b"")
    elem_data_single_string(meta_data, b"Subject", b"")
    elem_data_single_string(meta_data, b"Author", b"")
    elem_data_single_string(meta_data, b"Keywords", b"")
    elem_data_single_string(meta_data, b"Revision", b"")
    elem_data_single_string(meta_data, b"Comment", b"")

    props = elem_properties(scene_info)
    elem_props_set(props, "p_string_url", b"DocumentUrl", "/foobar.fbx")
    elem_props_set(props, "p_string_url", b"SrcDocumentUrl", "/foobar.fbx")
    original = elem_props_compound(props, b"Original")
    original("p_string", b"ApplicationVendor", app_vendor)
    original("p_string", b"ApplicationName", app_name)
    original("p_string", b"ApplicationVersion", app_ver)
    original("p_datetime", b"DateTime_GMT", "01/01/1970 00:00:00.000")
    original("p_string", b"FileName", "/foobar.fbx")
    lastsaved = elem_props_compound(props, b"LastSaved")
    lastsaved("p_string", b"ApplicationVendor", app_vendor)
    lastsaved("p_string", b"ApplicationName", app_name)
    lastsaved("p_string", b"ApplicationVersion", app_ver)
    lastsaved("p_datetime", b"DateTime_GMT", "01/01/1970 00:00:00.000")

    # ##### End of FBXHeaderExtension element.

    # FileID is replaced by dummy value currently...
    elem_data_single_bytes(root, b"FileId", b"FooBar")

    # CreationTime is replaced by dummy value currently, but anyway...
    elem_data_single_string_unicode(root, b"CreationTime",
                                    "{:04}-{:02}-{:02} {:02}:{:02}:{:02}:{:03}"
                                    "".format(time.year, time.month, time.day, time.hour, time.minute, time.second,
                                              time.microsecond * 1000))

    elem_data_single_string_unicode(root, b"Creator", "%s - %s - %d.%d.%d"
                                          % (app_name, app_ver, addon_ver[0], addon_ver[1], addon_ver[2]))

    # ##### Start of GlobalSettings element.
    global_settings = elem_empty(root, b"GlobalSettings")
    scene = scene_data.scene

    elem_data_single_int32(global_settings, b"Version", 1000)

    props = elem_properties(global_settings)
    up_axis, front_axis, coord_axis = RIGHT_HAND_AXES[scene_data.settings.to_axes]
    #~ # DO NOT take into account global scale here! That setting is applied to object transformations during export
    #~ # (in other words, this is pure blender-exporter feature, and has nothing to do with FBX data).
    #~ if scene_data.settings.apply_unit_scale:
        #~ # Unit scaling is applied to objects' scale, so our unit is effectively FBX one (centimeter).
        #~ scale_factor_org = 1.0
        #~ scale_factor = 1.0 / units_blender_to_fbx_factor(scene)
    #~ else:
        #~ scale_factor_org = units_blender_to_fbx_factor(scene)
        #~ scale_factor = scale_factor_org
    scale_factor = scale_factor_org = scene_data.settings.unit_scale
    elem_props_set(props, "p_integer", b"UpAxis", up_axis[0])
    elem_props_set(props, "p_integer", b"UpAxisSign", up_axis[1])
    elem_props_set(props, "p_integer", b"FrontAxis", front_axis[0])
    elem_props_set(props, "p_integer", b"FrontAxisSign", front_axis[1])
    elem_props_set(props, "p_integer", b"CoordAxis", coord_axis[0])
    elem_props_set(props, "p_integer", b"CoordAxisSign", coord_axis[1])
    elem_props_set(props, "p_integer", b"OriginalUpAxis", -1)
    elem_props_set(props, "p_integer", b"OriginalUpAxisSign", 1)
    elem_props_set(props, "p_double", b"UnitScaleFactor", scale_factor)
    elem_props_set(props, "p_double", b"OriginalUnitScaleFactor", scale_factor_org)
    elem_props_set(props, "p_color_rgb", b"AmbientColor", (0.0, 0.0, 0.0))
    elem_props_set(props, "p_string", b"DefaultCamera", "Producer Perspective")

    # Global timing data.
    r = scene.render
    _, fbx_fps_mode = FBX_FRAMERATES[0]  # Custom framerate.
    fbx_fps = fps = r.fps / r.fps_base
    for ref_fps, fps_mode in FBX_FRAMERATES:
        if similar_values(fps, ref_fps):
            fbx_fps = ref_fps
            fbx_fps_mode = fps_mode
    elem_props_set(props, "p_enum", b"TimeMode", fbx_fps_mode)
    elem_props_set(props, "p_timestamp", b"TimeSpanStart", 0)
    elem_props_set(props, "p_timestamp", b"TimeSpanStop", FBX_KTIME)
    elem_props_set(props, "p_double", b"CustomFrameRate", fbx_fps)

    # ##### End of GlobalSettings element.


