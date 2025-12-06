"""Utilities to manage Maya viewport override colors for shape nodes.

This module provides helpers for reading the current selection and applying or
resetting the Maya draw-override color on shape nodes. It is intended to run
inside Autodesk Maya with maya.cmds available.
"""

import maya.cmds as cmds
import maya.OpenMaya as om


class ColorHelper:
    """Helper methods for working with Maya's display override colors.

    Notes:
    - Maya supports 32 legacy index colors for overrides (0-31). See
      Window > Settings/Preferences > Color Settings for their mapping.
    - All functions operate on currently selected DAG nodes and affect
      their shape descendants (e.g., meshes, NURBS shapes).
    """

    MAX_OVERRIDE_COLORS = 32

    @classmethod
    def get_shape_nodes(cls):
        """Return shape nodes under the current selection.

        Returns:
            list[str] | None: A list of shape node names under the selected
            transforms, or None if nothing is selected.
        """
        selection = cmds.ls(selection=True)
        if not selection:
            return None

        shapes = []
        for node in selection:
            shapes.extend(cmds.listRelatives(node, shapes=True) or [])

        return shapes

    @classmethod
    def override_color(cls, color_index):
        """Enable draw overrides and set the overrideColor on selected shapes.

        Args:
            color_index (int): Index color in the range [0, 31].

        Returns:
            bool | None: False on validation/selection failure, otherwise None.
        """
        if color_index >= cls.MAX_OVERRIDE_COLORS or color_index < 0:
            om.MGlobal.displayError("Color index out-of-range (must be between 0-31)")
            return False

        shapes = cls.get_shape_nodes()
        if not shapes:
            om.MGlobal.displayError("No shape nodes selected")
            return False

        for shape in shapes:
            try:
                cmds.setAttr(f"{shape}.overrideEnabled", True)
                cmds.setAttr(f"{shape}.overrideColor", color_index)
            except RuntimeError:
                om.MGlobal.displayWarning("Failed to override color: {0}".format(shape))
        return None



