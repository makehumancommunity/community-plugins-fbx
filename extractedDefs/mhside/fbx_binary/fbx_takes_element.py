def fbx_takes_element(root):
    # TODO actually allow exporting takes, or is it not required (according to blender fbx authors)?
    # XXX Pretty sure takes are no more needed...
    takes = elem_empty(root, b"Takes")
    elem_data_single_string(takes, b"Current", b"")
