def fbx_data_element_custom_properties(props, bid):
    """
    Store custom properties of blender ID bid (any mapping-like object, in fact) into FBX properties props.
    """
    for k, v in bid.items():
        list_val = getattr(v, "to_list", lambda: None)()

        if isinstance(v, str):
            elem_props_set(props, "p_string", k.encode(), v, custom=True)
        elif isinstance(v, int):
            elem_props_set(props, "p_integer", k.encode(), v, custom=True)
        elif isinstance(v, float):
            elem_props_set(props, "p_double", k.encode(), v, custom=True)
        elif list_val:
            if len(list_val) == 3:
                elem_props_set(props, "p_vector", k.encode(), list_val, custom=True)
            else:
                elem_props_set(props, "p_string", k.encode(), str(list_val), custom=True)
        else:
            elem_props_set(props, "p_string", k.encode(), str(v), custom=True)


