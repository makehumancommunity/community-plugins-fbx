def fbx_template_def_camera(scene, settings, override_defaults=None, nbr_users=0):
    r = scene.render
    props = OrderedDict((
        (b"Color", ((0.8, 0.8, 0.8), "p_color_rgb", False)),
        (b"Position", ((0.0, 0.0, -50.0), "p_vector", True)),
        (b"UpVector", ((0.0, 1.0, 0.0), "p_vector", True)),
        (b"InterestPosition", ((0.0, 0.0, 0.0), "p_vector", True)),
        (b"Roll", (0.0, "p_roll", True)),
        (b"OpticalCenterX", (0.0, "p_opticalcenterx", True)),
        (b"OpticalCenterY", (0.0, "p_opticalcentery", True)),
        (b"BackgroundColor", ((0.63, 0.63, 0.63), "p_color", True)),
        (b"TurnTable", (0.0, "p_number", True)),
        (b"DisplayTurnTableIcon", (False, "p_bool", False)),
        (b"UseMotionBlur", (False, "p_bool", False)),
        (b"UseRealTimeMotionBlur", (True, "p_bool", False)),
        (b"Motion Blur Intensity", (1.0, "p_number", True)),
        (b"AspectRatioMode", (0, "p_enum", False)),  # WindowSize.
        (b"AspectWidth", (320.0, "p_double", False)),
        (b"AspectHeight", (200.0, "p_double", False)),
        (b"PixelAspectRatio", (1.0, "p_double", False)),
        (b"FilmOffsetX", (0.0, "p_number", True)),
        (b"FilmOffsetY", (0.0, "p_number", True)),
        (b"FilmWidth", (0.816, "p_double", False)),
        (b"FilmHeight", (0.612, "p_double", False)),
        (b"FilmAspectRatio", (1.3333333333333333, "p_double", False)),
        (b"FilmSqueezeRatio", (1.0, "p_double", False)),
        (b"FilmFormatIndex", (0, "p_enum", False)),  # Assuming this is ApertureFormat, 0 = custom.
        (b"PreScale", (1.0, "p_number", True)),
        (b"FilmTranslateX", (0.0, "p_number", True)),
        (b"FilmTranslateY", (0.0, "p_number", True)),
        (b"FilmRollPivotX", (0.0, "p_number", True)),
        (b"FilmRollPivotY", (0.0, "p_number", True)),
        (b"FilmRollValue", (0.0, "p_number", True)),
        (b"FilmRollOrder", (0, "p_enum", False)),  # 0 = rotate first (default).
        (b"ApertureMode", (2, "p_enum", False)),  # 2 = Vertical.
        (b"GateFit", (0, "p_enum", False)),  # 0 = no resolution gate fit.
        (b"FieldOfView", (25.114999771118164, "p_fov", True)),
        (b"FieldOfViewX", (40.0, "p_fov_x", True)),
        (b"FieldOfViewY", (40.0, "p_fov_y", True)),
        (b"FocalLength", (34.89327621672628, "p_number", True)),
        (b"CameraFormat", (0, "p_enum", False)),  # Custom camera format.
        (b"UseFrameColor", (False, "p_bool", False)),
        (b"FrameColor", ((0.3, 0.3, 0.3), "p_color_rgb", False)),
        (b"ShowName", (True, "p_bool", False)),
        (b"ShowInfoOnMoving", (True, "p_bool", False)),
        (b"ShowGrid", (True, "p_bool", False)),
        (b"ShowOpticalCenter", (False, "p_bool", False)),
        (b"ShowAzimut", (True, "p_bool", False)),
        (b"ShowTimeCode", (False, "p_bool", False)),
        (b"ShowAudio", (False, "p_bool", False)),
        (b"AudioColor", ((0.0, 1.0, 0.0), "p_vector_3d", False)),  # Yep, vector3d, not corlorgb… :cry:
        (b"NearPlane", (10.0, "p_double", False)),
        (b"FarPlane", (4000.0, "p_double", False)),
        (b"AutoComputeClipPanes", (False, "p_bool", False)),
        (b"ViewCameraToLookAt", (True, "p_bool", False)),
        (b"ViewFrustumNearFarPlane", (False, "p_bool", False)),
        (b"ViewFrustumBackPlaneMode", (2, "p_enum", False)),  # 2 = show back plane if texture added.
        (b"BackPlaneDistance", (4000.0, "p_number", True)),
        (b"BackPlaneDistanceMode", (1, "p_enum", False)),  # 1 = relative to camera.
        (b"ViewFrustumFrontPlaneMode", (2, "p_enum", False)),  # 2 = show front plane if texture added.
        (b"FrontPlaneDistance", (10.0, "p_number", True)),
        (b"FrontPlaneDistanceMode", (1, "p_enum", False)),  # 1 = relative to camera.
        (b"LockMode", (False, "p_bool", False)),
        (b"LockInterestNavigation", (False, "p_bool", False)),
        # BackPlate... properties **arggggg!**
        (b"FitImage", (False, "p_bool", False)),
        (b"Crop", (False, "p_bool", False)),
        (b"Center", (True, "p_bool", False)),
        (b"KeepRatio", (True, "p_bool", False)),
        # End of BackPlate...
        (b"BackgroundAlphaTreshold", (0.5, "p_double", False)),
        (b"ShowBackplate", (True, "p_bool", False)),
        (b"BackPlaneOffsetX", (0.0, "p_number", True)),
        (b"BackPlaneOffsetY", (0.0, "p_number", True)),
        (b"BackPlaneRotation", (0.0, "p_number", True)),
        (b"BackPlaneScaleX", (1.0, "p_number", True)),
        (b"BackPlaneScaleY", (1.0, "p_number", True)),
        (b"Background Texture", (None, "p_object", False)),
        (b"FrontPlateFitImage", (True, "p_bool", False)),
        (b"FrontPlateCrop", (False, "p_bool", False)),
        (b"FrontPlateCenter", (True, "p_bool", False)),
        (b"FrontPlateKeepRatio", (True, "p_bool", False)),
        (b"Foreground Opacity", (1.0, "p_double", False)),
        (b"ShowFrontplate", (True, "p_bool", False)),
        (b"FrontPlaneOffsetX", (0.0, "p_number", True)),
        (b"FrontPlaneOffsetY", (0.0, "p_number", True)),
        (b"FrontPlaneRotation", (0.0, "p_number", True)),
        (b"FrontPlaneScaleX", (1.0, "p_number", True)),
        (b"FrontPlaneScaleY", (1.0, "p_number", True)),
        (b"Foreground Texture", (None, "p_object", False)),
        (b"DisplaySafeArea", (False, "p_bool", False)),
        (b"DisplaySafeAreaOnRender", (False, "p_bool", False)),
        (b"SafeAreaDisplayStyle", (1, "p_enum", False)),  # 1 = rounded corners.
        (b"SafeAreaAspectRatio", (1.3333333333333333, "p_double", False)),
        (b"Use2DMagnifierZoom", (False, "p_bool", False)),
        (b"2D Magnifier Zoom", (100.0, "p_number", True)),
        (b"2D Magnifier X", (50.0, "p_number", True)),
        (b"2D Magnifier Y", (50.0, "p_number", True)),
        (b"CameraProjectionType", (0, "p_enum", False)),  # 0 = perspective, 1 = orthogonal.
        (b"OrthoZoom", (1.0, "p_double", False)),
        (b"UseRealTimeDOFAndAA", (False, "p_bool", False)),
        (b"UseDepthOfField", (False, "p_bool", False)),
        (b"FocusSource", (0, "p_enum", False)),  # 0 = camera interest, 1 = distance from camera interest.
        (b"FocusAngle", (3.5, "p_double", False)),  # ???
        (b"FocusDistance", (200.0, "p_double", False)),
        (b"UseAntialiasing", (False, "p_bool", False)),
        (b"AntialiasingIntensity", (0.77777, "p_double", False)),
        (b"AntialiasingMethod", (0, "p_enum", False)),  # 0 = oversampling, 1 = hardware.
        (b"UseAccumulationBuffer", (False, "p_bool", False)),
        (b"FrameSamplingCount", (7, "p_integer", False)),
        (b"FrameSamplingType", (1, "p_enum", False)),  # 0 = uniform, 1 = stochastic.
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"NodeAttribute", b"FbxCamera", props, nbr_users, [False])


