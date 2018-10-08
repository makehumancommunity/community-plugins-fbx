def fbx_data_camera_elements(root, cam_obj, scene_data):
    """
    Write the Camera data blocks.
    """
    gscale = scene_data.settings.global_scale

    cam = cam_obj.bdata
    cam_data = cam.data
    cam_key = scene_data.data_cameras[cam_obj]

    # Real data now, good old camera!
    # Object transform info.
    loc, rot, scale, matrix, matrix_rot = cam_obj.fbx_object_tx(scene_data)
    up = matrix_rot * Vector((0.0, 1.0, 0.0))
    to = matrix_rot * Vector((0.0, 0.0, -1.0))
    # Render settings.
    # TODO We could export much more...
    render = scene_data.scene.render
    width = render.resolution_x
    height = render.resolution_y
    aspect = width / height
    # Film width & height from mm to inches
    filmwidth = convert_mm_to_inch(cam_data.sensor_width)
    filmheight = convert_mm_to_inch(cam_data.sensor_height)
    filmaspect = filmwidth / filmheight
    # Film offset
    offsetx = filmwidth * cam_data.shift_x
    offsety = filmaspect * filmheight * cam_data.shift_y

    cam = elem_data_single_int64(root, b"NodeAttribute", get_fbx_uuid_from_key(cam_key))
    cam.add_string(fbx_name_class(cam_data.name.encode(), b"NodeAttribute"))
    cam.add_string(b"Camera")

    tmpl = elem_props_template_init(scene_data.templates, b"Camera")
    props = elem_properties(cam)

    elem_props_template_set(tmpl, props, "p_vector", b"Position", loc)
    elem_props_template_set(tmpl, props, "p_vector", b"UpVector", up)
    elem_props_template_set(tmpl, props, "p_vector", b"InterestPosition", loc + to)  # Point, not vector!
    # Should we use world value?
    elem_props_template_set(tmpl, props, "p_color", b"BackgroundColor", (0.0, 0.0, 0.0))
    elem_props_template_set(tmpl, props, "p_bool", b"DisplayTurnTableIcon", True)

    elem_props_template_set(tmpl, props, "p_enum", b"AspectRatioMode", 2)  # FixedResolution
    elem_props_template_set(tmpl, props, "p_double", b"AspectWidth", float(render.resolution_x))
    elem_props_template_set(tmpl, props, "p_double", b"AspectHeight", float(render.resolution_y))
    elem_props_template_set(tmpl, props, "p_double", b"PixelAspectRatio",
                            float(render.pixel_aspect_x / render.pixel_aspect_y))

    elem_props_template_set(tmpl, props, "p_double", b"FilmWidth", filmwidth)
    elem_props_template_set(tmpl, props, "p_double", b"FilmHeight", filmheight)
    elem_props_template_set(tmpl, props, "p_double", b"FilmAspectRatio", filmaspect)
    elem_props_template_set(tmpl, props, "p_double", b"FilmOffsetX", offsetx)
    elem_props_template_set(tmpl, props, "p_double", b"FilmOffsetY", offsety)

    elem_props_template_set(tmpl, props, "p_enum", b"ApertureMode", 3)  # FocalLength.
    elem_props_template_set(tmpl, props, "p_enum", b"GateFit", 2)  # FitHorizontal.
    elem_props_template_set(tmpl, props, "p_fov", b"FieldOfView", math.degrees(cam_data.angle_x))
    elem_props_template_set(tmpl, props, "p_fov_x", b"FieldOfViewX", math.degrees(cam_data.angle_x))
    elem_props_template_set(tmpl, props, "p_fov_y", b"FieldOfViewY", math.degrees(cam_data.angle_y))
    # No need to convert to inches here...
    elem_props_template_set(tmpl, props, "p_double", b"FocalLength", cam_data.lens)
    elem_props_template_set(tmpl, props, "p_double", b"SafeAreaAspectRatio", aspect)
    # Default to perspective camera.
    elem_props_template_set(tmpl, props, "p_enum", b"CameraProjectionType", 1 if cam_data.type == 'ORTHO' else 0)
    elem_props_template_set(tmpl, props, "p_double", b"OrthoZoom", cam_data.ortho_scale)

    elem_props_template_set(tmpl, props, "p_double", b"NearPlane", cam_data.clip_start * gscale)
    elem_props_template_set(tmpl, props, "p_double", b"FarPlane", cam_data.clip_end * gscale)
    elem_props_template_set(tmpl, props, "p_enum", b"BackPlaneDistanceMode", 1)  # RelativeToCamera.
    elem_props_template_set(tmpl, props, "p_double", b"BackPlaneDistance", cam_data.clip_end * gscale)

    elem_props_template_finalize(tmpl, props)

    # Custom properties.
    if scene_data.settings.use_custom_props:
        fbx_data_element_custom_properties(props, cam_data)

    elem_data_single_string(cam, b"TypeFlags", b"Camera")
    elem_data_single_int32(cam, b"GeometryVersion", 124)  # Sic...
    elem_data_vec_float64(cam, b"Position", loc)
    elem_data_vec_float64(cam, b"Up", up)
    elem_data_vec_float64(cam, b"LookAt", to)
    elem_data_single_int32(cam, b"ShowInfoOnMoving", 1)
    elem_data_single_int32(cam, b"ShowAudio", 0)
    elem_data_vec_float64(cam, b"AudioColor", (0.0, 1.0, 0.0))
    elem_data_single_float64(cam, b"CameraOrthoZoom", 1.0)


