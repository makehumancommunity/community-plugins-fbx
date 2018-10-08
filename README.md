# community-plugins-fbx

This is a port of Blender's FBX code. The aim is to provide an up-to-date FBX export functionality
for MakeHuman.

This code replaces the FBX plugin currently in the main repo.

## Timeline

Important dates / commits in the history of the FBX plugin (to be used for tracking down
changes against blender's code)

* 2014-11-09: Add support for binary FBX -- https://bitbucket.org/MakeHuman/makehuman/commits/9b404385ef38878705ededb9e42a74aeccf6debd 
* 2014-02-10: No fbx texture -- https://bitbucket.org/MakeHuman/makehuman/commits/ec9e4a7899893b96d6a24becde164b56f2017871
* 2014-02-02: (start of bitbucket history)

* 2014-03-19: Blender 2.70 released
* 2013-10-31: Blender 2.69 released

... However, the structure of the FBX directory is vastly different in both blender 2.70 and blender 2.69. This leads me to assume
that the code was not taken from a bundled FBX at the time. Rather there must've been an outside source of the code. 

The first blender release with a similar code structure is 2.71. We'll use that for comparisons.

## File mappings

The MH code has been refactored into files with different names than the blender ones. This is a map of which MH code files
map onto which blender ones, and to what extent.

### data_types.py

This is a 100% mapping onto the blender file with the same name.

### encode_bin.py

This is an almost 100% mapping onto the blender file, but with some modifications (which are probably only for py2 compat)

### fbx_anim.py

This is a mostly new file, but constants have been taken from blender's export_fbx_bin. Lines 57-78 MH side largely matches
lines 443-470 blender side for 2.71, and 474-501 for 2.79.

### fbx_binary.py

Large parts of this file matches blender's export_fbx_bin.py, but there are also huge differences. 

Functions that exist in blender but not in mh:

* check_skip_material.py
* defaults_unity3d.py
* fbx_animations_do.py
* fbx_animations.py
* fbx_connections_elements.py
* fbx_data_animation_elements.py
* fbx_data_armature_elements.py
* fbx_data_camera_elements.py
* fbx_data_empty_elements.py
* fbx_data_from_scene.py
* fbx_data_lamp_elements.py
* fbx_data_leaf_bone_elements.py
* fbx_data_material_elements.py
* fbx_data_mesh_elements.py
* fbx_data_mesh_shapes_elements.py
* fbx_data_object_elements.py
* fbx_data_texture_file_elements.py
* fbx_data_video_elements.py
* fbx_generate_leaf_bones.py
* fbx_mat_properties_from_texture.py
* fbx_objects_elements.py
* fbx_scene_data_cleanup.py
* fbx_skeleton_from_armature.py
* fbx_takes_elements.py
* fbx_template_def_camera.py
* fbx_template_def_light.py
* fbx_template_def_model.py
* fbx_template_def_video.py
* _gen_vid_path.py
* save.py
* save_single.py

Functions that exist in mh but not in blender:

* fbx_connections_element.py
* fbx_data_deformer.py
* fbx_data_material.py
* fbx_data_mesh_element.py
* fbx_data_model_element.py
* fbx_data_pose_node_element.py
* fbx_data_skeleton_bone_model.py
* fbx_data_skeleton_bone_node.py
* fbx_data_skeleton_model.py
* fbx_data_subdeformer.py
* fbx_data_texture_file_element.py
* fbx_takes_element.py

### fbx_deformer.py

### fbx_header.py

### fbx_material.py

### fbx_mesh.py

### fbx_skeleton.py

### fbx_utils_bin.py

### fbx_utils.py

### __init__.py

### mh2fbx.py





