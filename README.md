# BlenDir <!-- omit in toc -->

**BlenDir** is a Blender add-on for automatic folder structure creation!

![BlenDir Addon](docs/blendir.PNG)

---

## Table of Contents <!-- omit in toc -->

- [Features](#features)
  - [Create complex project folder structure in one click](#create-complex-project-folder-structure-in-one-click)
  - [Easily browse saved folder structures](#easily-browse-saved-folder-structures)
  - [Generate folder structure files from existing directories](#generate-folder-structure-files-from-existing-directories)
  - [Keywords](#keywords)
  - [Make custom folder structures](#make-custom-folder-structures)
  - [Edit saved folder structures](#edit-saved-folder-structures)
  - [Delete saved folder structures](#delete-saved-folder-structures)
  - [Open project location](#open-project-location)
  - [Save startup settings](#save-startup-settings)
- [Installation](#installation)

---

## Features

---

### Create complex project folder structure in one click

![Create Folders](docs/create_folders.PNG)

### Easily browse saved folder structures

![Browse](docs/browse.PNG)

### Generate folder structure files from existing directories

- Click ![Import Structure](docs/import.PNG)
- Use the directory browser to select a root folder
![Directory Browser](docs/directory_browser.PNG)
- The complete folder structure file will be generated automatically
- This file can be used to recreate the saved structure with one click

### Keywords

Add keywords to program the folder structure generator!

- `*B` Move Blender file to this directory
- `*F` Current file name
- `*D` Current date
- `*X` `*Y` `*Z` Custom input

### Make custom folder structures

- Click ![New Structure](docs/new_structure.PNG)
- After entering the name, the new structure will open in your default text editor
![New Popup](docs/new_popup.PNG)
- Choose `Use Template` to start with extra information about how to create the structure
![Template](docs/template.PNG)

### Edit saved folder structures

- Click ![Edit](docs/edit.PNG)
- The structure will open in the default text editor

### Delete saved folder structures

- Click ![Delete](docs/delete.PNG)

### Open project location

- Click ![Open](docs/open.PNG)
- The location of the current Blender file will open in the file browser

### Save startup settings

- Click ![Save Settings](docs/save_settings.PNG)
- The current settings will be saved and loaded when starting Blender

(For more information, read the tooltips/descriptions of the buttons and settings)

---

## Installation

---

- Download the `ZIP` file (don't extract it)

![Download](docs/download.PNG) ![ZIP](docs/zip.PNG)

- In Blender, open `Preferences` and go to `Add-ons`
- Click `Install`
- Select the `ZIP` file in the file browser
- Click `Install Add-on`
- Enable the add-on by checking the box

![Enable](docs/enable.PNG)
