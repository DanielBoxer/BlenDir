# BlenDir v0.18.2 <!-- omit in toc -->

**BlenDir** is a Blender add-on for automatic folder structure creation and management!

<img align="right" src="docs/blendir.PNG">

## Table of Contents <!-- omit in toc -->

- [Features](#features)
  - [One Click Project Folder Structure](#one-click-project-folder-structure)
  - [Make Custom Folder Structures](#make-custom-folder-structures)
  - [Bookmarks](#bookmarks)
  - [References Menu](#references-menu)
  - [Auto Save Image Renders](#auto-save-image-renders)
  - [Animation Frames Folders](#animation-frames-folders)
  - [Keywords](#keywords)
  - [Keymap](#keymap)
- [Setup Instructions](#setup-instructions)
- [General Instructions](#general-instructions)
  - [Automatically Generate Folder Structure Files](#automatically-generate-folder-structure-files)
- [Installation](#installation)
  - [Method 1 (recommended)](#method-1-recommended)
  - [Method 2](#method-2)
- [Notes](#notes)

## Features

### One Click Project Folder Structure

![BlenDir](https://user-images.githubusercontent.com/65575771/171467683-33cff7dd-3283-49f4-96e9-62ec3184f878.gif)

### Make Custom Folder Structures

- Automatically [generate](#generate-folder-structure-files-from-existing-directories) folder structures or make them from scratch
- Add functionality with [keywords](#keywords)
- Easily browse your saved folder structures

![Browse](docs/browse.PNG)

### Bookmarks

- Add local and global folder bookmarks. Selecting a bookmark will open it in the default OS file browser

![Bookmarks](docs/bookmarks.PNG)

### References Menu

- Quickly open your project references with a pie menu

![References](docs/references.PNG)

### Auto Save Image Renders

- Automatically save image renders to your render folder

![Auto Save Image](https://user-images.githubusercontent.com/65575771/172444114-f999af6f-bfbc-4aad-9d0d-56bb9e1d1737.gif)

### Animation Frames Folders

- When an animation is rendered, a subfolder will be automatically created in the render folder for the frames of the animation

![Animation Folders](https://user-images.githubusercontent.com/65575771/172444538-713edd96-4969-4d76-bd6e-bf8c1cd42407.gif)

### Keywords

- Add keywords to program the folder structure generator and add extra features to your folder structures!

  - `*B` Move the Blender file to this folder
  - `*F` Replaced with the current Blender file name
  - `*D` Replaced with the current date
  - `*X` `*Y` `*Z` Replaced with input from the preferences
  - `*M` Bookmark this folder. This will add the folder to the `Bookmarks` pie menu for this project only
  - `*R` Mark this folder as the reference folder. All files added to this folder will show up in the `References` pie menu
  - `*O` Set the animation output path to this folder. This will also be used to automatically save image renders.

### Keymap

- Use shortcuts to make creating folders even quicker

![Keymap](docs/keymap.PNG)

## Setup Instructions

1. Delete the `Animation` and `Example` demo structures that come with BlenDir (use the BlenDir delete button)
2. Click the [import](#generate-folder-structure-files-from-existing-directories) button or the new structure button to create a folder structure file
3. Add [keywords](#keywords) to the file for custom functionality. For example:

     - replace the root folder name with `*F*B`
     - add `*M` to all folders you want to bookmark
     - add `*R` to your references folder
     - add `*O` to your render folder

## General Instructions

### Automatically Generate Folder Structure Files

- Click ![Import Structure](docs/import.PNG)
- Use the directory browser to select an existing root folder

![Directory Browser](docs/directory_browser.PNG)

- The complete folder structure file will be generated automatically
- This file can be used to recreate the saved folder structure

## Installation

### Method 1 (recommended)

- Download the `ZIP` file (don't extract it)
  - Either go to [Releases](https://github.com/DanielBoxer/BlenDir/releases/latest) and download the `ZIP` file for the latest stable version
  - Or press the `Code` button at the top of the page and then `Download ZIP` for the newest experimental version

- Don't add a `.` to the folder name, this will cause an import error
- In Blender, open `Preferences` and go to `Add-ons`
- Click `Install`
- Select the `ZIP` file in the file browser
- Click `Install Add-on`
- Enable the add-on by checking the box

### Method 2

- Download BlenDir
- Extract the `ZIP` file
- Move the folder inside the extracted folder into your Blender `addons` directory
- Enable BlenDir

## Notes

- BlenDir is for Blender version 2.90 and above
- Works on Windows and Linux, untested on macOS
