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


