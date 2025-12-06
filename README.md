# MAR Tools

A collection of PySide6-based tools designed for Autodesk Maya workflows.

## Tools Included

### Orienter

Interactively orient joints with control over Aim/Up axes, world-up direction, auto-orient secondary axis, manual tweaks,
and visibility control for selected or all joints in the scene.

![Description](docs/images/MAR%20Tools%20Orienter%20Screenshot.png)

### Spawner

Spawn skinned FK curve controls, utility meshes for visual debugging, and joints from selected rivet/pivot constraints. 

![Description](docs/images/MAR%20Tools%20Spawner%20Screenshot.png)

### Colorizer

Apply viewport override index colors to selected shape nodes and vertex colors for mesh ID that can be used in Substance
Painter.

![Description](docs/images/MAR%20Tools%20Colorizer%20Screenshot.png)

...and more to come!

## Requirements
- Autodesk Maya 2025 or later.

## Installation

1. [Click Here to Download MAR Tools](https://github.com/marairanti/mar-tools/releases/download/v0.1.0/mar-tools-v0.1.0.zip)
2. Extract the contents to:
    - Windows: "C:/Users/{username}/maya/scripts/"
    - macOS: "/Users/{username}/Library/Preferences/Autodesk/maya/scripts/"
    - Linux: "/home/{username}/maya/scripts/"
3. In userSetup.mel, add the following line:

```mel
python("import mar_tools_loader");
```

## Usage (inside Maya)
By default, the menu MAR Tools will be added to the Maya main menu.

![Description](docs/images/MAR%20Tools%20Menu%20Screenshot.png)

Pressing Ctrl+Shift+Left-Click on the selected tool will create a new shelf button.

Alternatively, you can add the following snippets to a Maya shelf button for quick access:

```python
from tool.orienter import OrienterWidget; OrienterWidget.show_dialog()
```

```python
from tool.spawner import SpawnerWidget; SpawnerWidget.show_dialog()
```

```python
from tool.colorizer import ColorizerWidget; ColorizerWidget.show_dialog()
```


## Notes
 
- MAR Tools are only compatible with Maya 2025/2026 and onwards as there are maya.cmds functions that are not available
  in earlier versions.
- Still in early development and may contain bugs.

