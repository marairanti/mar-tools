"""Joint utilities used by tools for selection, orientation, and cleanup.

This module wraps common operations on Maya joints (cmds.joint) that are used by
UI tools such as the Orienter. It requires running inside Autodesk Maya with
maya.cmds available.
"""

import maya.cmds as cmds


class JointHelper:
    """Helpers to query joints and perform orientation-related edits."""

    @classmethod
    def get_joints(cls, hierarchy=False, all_joints=False):
        """Get joints to operate on based on current selection and options.

        Args:
            hierarchy (bool): Include all descendant joints of the selection.
            all_joints (bool): Ignore selection and return all joints in the scene.

        Returns:
            list[str]: A list of joint DAG paths/names; empty if none is found.
        """

        if all_joints:
            return cmds.ls(type="joint") or []

        selected_joints = cmds.ls(selection=True, type="joint") or []
        if hierarchy and selected_joints:
            descendants = cmds.listRelatives(selected_joints, allDescendents=True, type="joint")[::-1] or []
            selected_joints.extend(descendants)

        return selected_joints

    @classmethod
    def freeze_joint_orientation(cls, joints_to_orient):
        """Zero out jointOrient and bake the rotation into the joint's transform.

        Args:
            joints_to_orient (str | list[str]): Joint name(s) to freeze.
        """
        cmds.joint(joints_to_orient, edit=True, zeroScaleOrient=True)
        cmds.makeIdentity(joints_to_orient, apply=True, translate=False, rotate=True, scale=False, normal=0)


