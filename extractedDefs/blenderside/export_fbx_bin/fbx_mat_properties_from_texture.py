def fbx_mat_properties_from_texture(tex):
    """
    Returns a set of FBX metarial properties that are affected by the given texture.
    Quite obviously, this is a fuzzy and far-from-perfect mapping! Amounts of influence are completely lost, e.g.
    Note tex is actually expected to be a texture slot.
    """
    # Mapping Blender -> FBX (blend_use_name, blend_fact_name, fbx_name).
    blend_to_fbx = (
        # Lambert & Phong...
        ("diffuse", "diffuse", b"DiffuseFactor"),
        ("color_diffuse", "diffuse_color", b"DiffuseColor"),
        ("alpha", "alpha", b"TransparencyFactor"),
        ("diffuse", "diffuse", b"TransparentColor"),  # Uses diffuse color in Blender!
        ("emit", "emit", b"EmissiveFactor"),
        ("diffuse", "diffuse", b"EmissiveColor"),  # Uses diffuse color in Blender!
        ("ambient", "ambient", b"AmbientFactor"),
        # ("", "", b"AmbientColor"),  # World stuff in Blender, for now ignore...
        ("normal", "normal", b"NormalMap"),
        # Note: unsure about those... :/
        # ("", "", b"Bump"),
        # ("", "", b"BumpFactor"),
        # ("", "", b"DisplacementColor"),
        # ("", "", b"DisplacementFactor"),
        # Phong only.
        ("specular", "specular", b"SpecularFactor"),
        ("color_spec", "specular_color", b"SpecularColor"),
        # See Material template about those two!
        ("hardness", "hardness", b"Shininess"),
        ("hardness", "hardness", b"ShininessExponent"),
        ("mirror", "mirror", b"ReflectionColor"),
        ("raymir", "raymir", b"ReflectionFactor"),
    )

    tex_fbx_props = set()
    for use_map_name, name_factor, fbx_prop_name in blend_to_fbx:
        # Always export enabled textures, even if they have a null influence...
        if getattr(tex, "use_map_" + use_map_name):
            tex_fbx_props.add(fbx_prop_name)

    return tex_fbx_props


