def check_skip_material(mat):
    """Simple helper to check whether we actually support exporting that material or not"""
    return mat.type not in {'SURFACE'} or mat.use_nodes


