def fbx_scene_data_cleanup(scene_data):
    """
    Some final cleanup...
    """
    # Delete temp meshes.
    done_meshes = set()
    for me_key, me, free in scene_data.data_meshes.values():
        if free and me_key not in done_meshes:
            bpy.data.meshes.remove(me)
            done_meshes.add(me_key)


