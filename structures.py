# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

STRUCTURES = {
    # Keywords (case sensitive):
    #
    # "\t" - adding a tab means a level of depth
    #      -> use tabs to create subfolders
    #
    # Optional:
    #
    # "*B" - where the blender file is moved to
    #      -> add this somewhere in the line (ex. "FolderName*B")
    #      -> if not added, the file will stay in or be moved to the root folder
    #      -> this will be removed from the folder name before creating the folder
    #      -> backup blender files will be moved too (.blend1, .blend2 ...)
    #
    # "*F" - will be replaced with the name of the blender file
    #      -> ex. "FolderName_*F",  becomes "FolderName_FileName"
    #
    # "*X", "*Y", "*Z" - will be replaced with custom input from the UI
    #
    # "*D" - replaced with the current date
    #
    # some example structures:
    "Template": [
        # main folder
        "Folder",
        # create subfolder with one level of depth (Folder > SubFolder1)
        "\tSubFolder1",
        # two levels of depth (Folder > SubFolder1 > SubFolder1A)
        "\t\tSubFolder1A",
        # (Folder > SubFolder1 > SubFolder1B)
        "\t\tSubFolder1B",
        "\t\t\tSubFolder1B-1",
        "\tSubFolder2",
        "\t\tSubFolder2A",
        "\tSubFolder3",
        "\t\tSubFolder3A",
        "\t\t\tSubFolder3A-1",
        "\t\t\tSubFolder3A-2",
        "\t\tSubFolder3B",
    ],
    "Default": [
        # add the current file name and move the blender file here
        "*F*B",
        "\tAssets",
        "\t\tModels",
        "\t\tTextures",
        "\tReferences",
        "\tRendered",
    ],
    "Animation": [
        "*F*B",
        "\tAssets",
        "\t\tModels",
        "\t\tTextures",
        "\tReferences",
        # add the current date after "Rendered_"
        "\tRendered_*D",
        "\t\tFrames",
        "\t\t\t1",
    ],
}
