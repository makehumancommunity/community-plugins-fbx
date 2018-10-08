def fbx_template_def_model(scene, settings, override_defaults=None, nbr_users=0):
    gscale = settings.global_scale
    props = OrderedDict((
        # Name,                   Value, Type, Animatable
        (b"QuaternionInterpolate", (0, "p_enum", False)),  # 0 = no quat interpolation.
        (b"RotationOffset", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"ScalingOffset", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"ScalingPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TranslationActive", (False, "p_bool", False)),
        (b"TranslationMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TranslationMax", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TranslationMinX", (False, "p_bool", False)),
        (b"TranslationMinY", (False, "p_bool", False)),
        (b"TranslationMinZ", (False, "p_bool", False)),
        (b"TranslationMaxX", (False, "p_bool", False)),
        (b"TranslationMaxY", (False, "p_bool", False)),
        (b"TranslationMaxZ", (False, "p_bool", False)),
        (b"RotationOrder", (0, "p_enum", False)),  # we always use 'XYZ' order.
        (b"RotationSpaceForLimitOnly", (False, "p_bool", False)),
        (b"RotationStiffnessX", (0.0, "p_double", False)),
        (b"RotationStiffnessY", (0.0, "p_double", False)),
        (b"RotationStiffnessZ", (0.0, "p_double", False)),
        (b"AxisLen", (10.0, "p_double", False)),
        (b"PreRotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"PostRotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationActive", (False, "p_bool", False)),
        (b"RotationMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationMax", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationMinX", (False, "p_bool", False)),
        (b"RotationMinY", (False, "p_bool", False)),
        (b"RotationMinZ", (False, "p_bool", False)),
        (b"RotationMaxX", (False, "p_bool", False)),
        (b"RotationMaxY", (False, "p_bool", False)),
        (b"RotationMaxZ", (False, "p_bool", False)),
        (b"InheritType", (0, "p_enum", False)),  # RrSs
        (b"ScalingActive", (False, "p_bool", False)),
        (b"ScalingMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"ScalingMax", ((1.0, 1.0, 1.0), "p_vector_3d", False)),
        (b"ScalingMinX", (False, "p_bool", False)),
        (b"ScalingMinY", (False, "p_bool", False)),
        (b"ScalingMinZ", (False, "p_bool", False)),
        (b"ScalingMaxX", (False, "p_bool", False)),
        (b"ScalingMaxY", (False, "p_bool", False)),
        (b"ScalingMaxZ", (False, "p_bool", False)),
        (b"GeometricTranslation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"GeometricRotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"GeometricScaling", ((1.0, 1.0, 1.0), "p_vector_3d", False)),
        (b"MinDampRangeX", (0.0, "p_double", False)),
        (b"MinDampRangeY", (0.0, "p_double", False)),
        (b"MinDampRangeZ", (0.0, "p_double", False)),
        (b"MaxDampRangeX", (0.0, "p_double", False)),
        (b"MaxDampRangeY", (0.0, "p_double", False)),
        (b"MaxDampRangeZ", (0.0, "p_double", False)),
        (b"MinDampStrengthX", (0.0, "p_double", False)),
        (b"MinDampStrengthY", (0.0, "p_double", False)),
        (b"MinDampStrengthZ", (0.0, "p_double", False)),
        (b"MaxDampStrengthX", (0.0, "p_double", False)),
        (b"MaxDampStrengthY", (0.0, "p_double", False)),
        (b"MaxDampStrengthZ", (0.0, "p_double", False)),
        (b"PreferedAngleX", (0.0, "p_double", False)),
        (b"PreferedAngleY", (0.0, "p_double", False)),
        (b"PreferedAngleZ", (0.0, "p_double", False)),
        (b"LookAtProperty", (None, "p_object", False)),
        (b"UpVectorProperty", (None, "p_object", False)),
        (b"Show", (True, "p_bool", False)),
        (b"NegativePercentShapeSupport", (True, "p_bool", False)),
        (b"DefaultAttributeIndex", (-1, "p_integer", False)),
        (b"Freeze", (False, "p_bool", False)),
        (b"LODBox", (False, "p_bool", False)),
        (b"Lcl Translation", ((0.0, 0.0, 0.0), "p_lcl_translation", True)),
        (b"Lcl Rotation", ((0.0, 0.0, 0.0), "p_lcl_rotation", True)),
        (b"Lcl Scaling", ((1.0, 1.0, 1.0), "p_lcl_scaling", True)),
        (b"Visibility", (1.0, "p_visibility", True)),
        (b"Visibility Inheritance", (1, "p_visibility_inheritance", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Model", b"FbxNode", props, nbr_users, [False])


