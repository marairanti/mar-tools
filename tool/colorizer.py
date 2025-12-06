"""
Colorizer Tool:

This tool provides functionality to set Maya shape override colors and vertex colors 
using a color palette interface. It supports two main workflows:

Features:
    - Apply index colors (0-31) to selected shapes
    - Generate random vertex colors for mesh ID used in Substance Painter
    - Restore Maya default shape colors
    - Dockable color palette UI with 32 color swatches

Usage:
    1. Select objects in Maya
    2. Click a color swatch to apply override color
    3. Use 'Set to Default' to restore Maya defaults
    4. 'Generate Mesh ID' creates random vertex colors
    5. 'Delete Mesh ID' removes vertex colors

Color Types:
    - Shape Override Colors: Maya's built-in 32 index colors
    - Mesh ID Colors: Random vertex colors for mesh ID used in Substance Painter

Requirements:
    - Valid mesh node selection in Maya scene
    - Meshes must support vertex colors for Mesh ID feature
"""

import maya.cmds as cmds
import maya.OpenMaya as om

from ui.widgets import CustomPushButton, CustomDialog, QtWidgets
from core.color import ColorHelper
import random


class ColorizerWidget(CustomDialog):
    OBJECT_NAME = "Colorizer"

    def __init__(self, parent=None):
        """Construct the UI and set up an internal state."""
        super().__init__(parent)
        self.setObjectName(self.OBJECT_NAME)

        self.selected_index = -1
        self.color_buttons = []
        self.base_styles = []

        self.palette_widget = None
        self.grid_layout = None
        self.default_button = None
        self.generate_mesh_id = None
        self.delete_mesh_id = None


        self.setup_ui()

    def create_widgets(self):
        """Create the palette grid and action buttons."""
        self.palette_widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.palette_widget)
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        columns = ColorHelper.MAX_OVERRIDE_COLORS // 4  # 8 columns, 4 rows
        color_swatch_size = 30

        for index in range(ColorHelper.MAX_OVERRIDE_COLORS):
            button = QtWidgets.QPushButton(self.palette_widget)
            button.setFlat(True)
            button.setFixedSize(color_swatch_size, color_swatch_size)

            if index == 0:
                color = [0.6, 0.6, 0.6]
            else:
                color = cmds.colorIndex(index, query=True)

            r = int(color[0] * 255)
            g = int(color[1] * 255)
            b = int(color[2] * 255)

            base_style = f"background-color: rgb({r}, {g}, {b}); border: none;"
            button.setStyleSheet(base_style)
            self.base_styles.append(base_style)

            button.clicked.connect(lambda checked=False, i=index: self.select_color(i))

            row = index // columns
            col = index % columns
            self.grid_layout.addWidget(button, row, col)

            self.color_buttons.append(button)

        self.default_button = CustomPushButton("Set to Default")
        self.generate_mesh_id = CustomPushButton("Generate Mesh ID")
        self.delete_mesh_id = CustomPushButton("Delete Mesh ID")

    def create_layout(self):
        """Lay out the palette and action buttons."""
        shape_colorizer_layout = QtWidgets.QVBoxLayout()
        shape_colorizer_layout.addWidget(self.palette_widget)
        shape_colorizer_layout.addWidget(self.default_button)

        shape_colorizer_grp = QtWidgets.QGroupBox("Shape Colors")
        shape_colorizer_grp.setLayout(shape_colorizer_layout)

        mesh_id_colorizer_layout = QtWidgets.QVBoxLayout()
        mesh_id_colorizer_layout.addWidget(self.generate_mesh_id)
        mesh_id_colorizer_layout.addWidget(self.delete_mesh_id)

        mesh_id_colorizer_grp = QtWidgets.QGroupBox("Mesh ID Colors")
        mesh_id_colorizer_grp.setLayout(mesh_id_colorizer_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(shape_colorizer_grp)
        main_layout.addWidget(mesh_id_colorizer_grp)
        main_layout.addStretch()

        # UI Tests
        # self.adjustSize()
        # self.setFixedSize(self.size())

    def create_connections(self):
        """Connect button clicks to actions."""
        self.default_button.clicked.connect(self.use_defaults)
        self.generate_mesh_id.clicked.connect(self.colorize_mesh_id)
        self.delete_mesh_id.clicked.connect(self.decolorize_mesh_id)

    def select_color(self, index):
        """Set the currently selected color index and update button highlight.

        Also, immediately applies the color to the current selection.
        """
        self.selected_index = index
        # Highlight the selected button
        for i, btn in enumerate(self.color_buttons):
            if i == index:
                selected_style = self.base_styles[i].replace("border: none;", "border: 2px solid white;")
                btn.setStyleSheet(selected_style)
            else:
                btn.setStyleSheet(self.base_styles[i])
        # Immediately apply the selected color
        self.colorize_shape()

    def colorize_shape(self):
        """Apply the selected color index to currently selected shapes."""
        cmds.undoInfo(openChunk=True)
        if self.selected_index != -1:
            ColorHelper.override_color(self.selected_index)
        cmds.undoInfo(closeChunk=True)

    @staticmethod
    def colorize_mesh_id():
        """Generate random mesh ID among separated meshes in the scene."""
        cmds.undoInfo(openChunk=True)

        preset_colors = [

            (1.0, 0.0, 0.0),  # Pure Red
            (0.0, 1.0, 0.0),  # Pure Green
            (0.0, 0.0, 1.0),  # Pure Blue
            (1.0, 1.0, 0.0),  # Pure Yellow
            (0.0, 1.0, 1.0),  # Pure Cyan
            (1.0, 0.0, 1.0),  # Pure Magenta
            (1.0, 0.5, 0.0),  # Saturated Orange
            (0.5, 0.0, 1.0),  # Saturated Purple (Violet)
            (0.0, 1.0, 0.5),  # Saturated Spring Green
            (0.5, 1.0, 0.0),  # Saturated Chartreuse
            (1.0, 0.0, 0.5),  # Saturated Rose
            (0.5, 0.0, 0.0),  # Dark Red
            (0.0, 0.5, 0.0),  # Dark Green
            (0.0, 0.0, 0.5),  # Dark Blue
        ]

        # Determine target meshes: use selection if it yields meshes, otherwise all meshes in the scene.
        selected_meshes = cmds.ls(selection=True, dagObjects=True, shapes=True, long=True, type='mesh') or []
        if not selected_meshes:
            selected_meshes = cmds.ls(type='mesh', long=True) or []

        if not selected_meshes:
            om.MGlobal.displayWarning("No mesh objects found in the scene.")
            return

        # Process Each Mesh Object
        for mesh_shape in selected_meshes:

            transform_node = cmds.listRelatives(mesh_shape, parent=True, fullPath=True)[0]

            random_color = random.choice(preset_colors)
            r, g, b = random_color

            try:
                cmds.select(transform_node, replace=True)
                cmds.polyColorPerVertex(
                    colorRGB=(r, g, b),
                    colorDisplayOption=True,
                )

            except Exception as e:
                om.MGlobal.displayError(f"Could not process mesh {transform_node}: {e}")

        cmds.undoInfo(closeChunk=True)

    @staticmethod
    def decolorize_mesh_id():
        """Delete mesh ID from the selected meshes in the scene."""
        cmds.undoInfo(openChunk=True)

        # Determine target meshes: use selection if it yields meshes, otherwise all meshes in the scene.
        selected_meshes = cmds.ls(selection=True, dagObjects=True, shapes=True, long=True, type='mesh') or []
        if not selected_meshes:
            # No meshes found under selection, fall back to all meshes in the scene
            selected_meshes = cmds.ls(type='mesh', long=True) or []

        if not selected_meshes:
            om.MGlobal.displayWarning("No mesh objects found in the scene.")
            return

        for mesh_shape in selected_meshes:
            cmds.polyColorPerVertex(mesh_shape, remove=True)


        cmds.undoInfo(closeChunk=True)

    def keyPressEvent(self, e):
        """Reserved for keyboard shortcut overrides (optional)."""
        pass

    @staticmethod
    def use_defaults():
        """Disable draw overrides on selected shapes, restoring Maya defaults.

        Returns:
            bool | None: False if nothing to operate on, otherwise None.
        """
        shapes = ColorHelper.get_shape_nodes()
        if not shapes:
            om.MGlobal.displayWarning("No shapes nodes selected")
            return False

        for shape in shapes:
            try:
                # noinspection PyTypeChecker
                cmds.setAttr(f"{shape}.overrideEnabled", False)
            except RuntimeError:
                om.MGlobal.displayError(f"Failed to restore defaults: {shape}")
        return None

if __name__ == "__main__":
    workspace_control_name = f"{ColorizerWidget.OBJECT_NAME}WorkspaceControl"

    if cmds.workspaceControl(workspace_control_name, exists=True):
        cmds.workspaceControl(workspace_control_name, edit=True, close=True)
        cmds.deleteUI(workspace_control_name)

    window = ColorizerWidget()
    window.show(dockable=True)