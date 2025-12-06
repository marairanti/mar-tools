"""
Spawner Tool:

This tool provides functionality to automatically create and assign curve controls 
to Maya joints, streamlining the rigging process. It supports two main workflows:

Features:
    - Spawn controls on selected joints or entire joint hierarchies
    - Pre-configured curve controls for spine and arm setups
    - Automatic naming and hierarchy organization
    - Maintains proper joint suffixes (_jnt)
    - Creates control groups for each joint

Usage:
    1. Select target joint(s) in Maya
    2. Choose spawn mode (Hierarchy/Selected)
    3. Click the desired control type button (Spine/Neck or Arm)

Control Naming Convention:
    - Transform nodes: <joint_name>_grp
    - Curve nodes: <joint_name>_crv

Requirements:
    - Joints must have '_jnt' suffix
    - Valid joint selection in the Maya scene
"""
import maya.cmds as cmds
import maya.OpenMaya as om
from maya.app.renderSetup.views.utils import Separator
from core.joint import JointHelper
from ui.widgets import CustomPushButton, CustomDialog, QtWidgets
from ui.elements import Separator
from assets.curves import spine_fk_curve, arm_fk_curve, finger_fk_curve

class SpawnerWidget(CustomDialog):
    OBJECT_NAME = "Spawner"

    def __init__(self):
        super().__init__()
        self.setObjectName(self.OBJECT_NAME)

        self.spawn_target_fk_hierarchy_rb = None
        self.spawn_target_fk_selected_rb = None
        self.spawn_spine_controls_btn = None
        self.spawn_arm_controls_btn = None
        self.spawn_finger_controls_btn = None
        self.spawn_cubes_btn = None
        self.delete_util_meshes_btn = None
        self.spawn_target_util_mesh_selected_rb = None
        self.spawn_target_util_mesh_hierarchy_rb = None
        self.spawn_rivet_joint_btn = None
        self.spawn_center_mesh_joint_btn = None

        self.setup_ui()

    def create_widgets(self):
        """Create the action buttons."""
        self.spawn_target_fk_hierarchy_rb = QtWidgets.QRadioButton("Hierarchy")
        self.spawn_target_fk_hierarchy_rb.setChecked(True)
        self.spawn_target_fk_selected_rb = QtWidgets.QRadioButton("Selected")
        self.spawn_spine_controls_btn = CustomPushButton("Spawn Spine/Neck FK Controls")
        self.spawn_arm_controls_btn = CustomPushButton("Spawn Arm/Leg FK Controls")
        self.spawn_finger_controls_btn = CustomPushButton("Spawn Finger FK Controls")

        self.spawn_target_util_mesh_hierarchy_rb = QtWidgets.QRadioButton("Hierarchy")
        self.spawn_target_util_mesh_hierarchy_rb.setChecked(True)
        self.spawn_target_util_mesh_selected_rb = QtWidgets.QRadioButton("Selected")
        self.spawn_cubes_btn = CustomPushButton("Spawn Utility Cubes")
        self.delete_util_meshes_btn = CustomPushButton("Delete Utility Meshes")

        self.spawn_rivet_joint_btn = CustomPushButton("Spawn Rivet Joint")
        self.spawn_center_mesh_joint_btn = CustomPushButton("Spawn Joint on Pivot")

    def create_layout(self):
        """Lay out the action buttons."""
        spawn_curve_target_layout = QtWidgets.QHBoxLayout()
        spawn_curve_target_layout.addWidget(self.spawn_target_fk_hierarchy_rb)
        spawn_curve_target_layout.addWidget(self.spawn_target_fk_selected_rb)

        spawn_curve_controls_layout = QtWidgets.QFormLayout()
        spawn_curve_controls_layout.addRow("Target:", spawn_curve_target_layout)
        spawn_curve_controls_layout.addRow(Separator())
        spawn_curve_controls_layout.addRow(self.spawn_spine_controls_btn)
        spawn_curve_controls_layout.addRow(self.spawn_arm_controls_btn)
        spawn_curve_controls_layout.addRow(self.spawn_finger_controls_btn)

        spawn_util_target_layout = QtWidgets.QHBoxLayout()
        spawn_util_target_layout.addWidget(self.spawn_target_util_mesh_hierarchy_rb)
        spawn_util_target_layout.addWidget(self.spawn_target_util_mesh_selected_rb)

        spawn_util_mesh_layout = QtWidgets.QFormLayout()
        spawn_util_mesh_layout.addRow("Target:", spawn_util_target_layout)
        spawn_util_mesh_layout.addRow(Separator())
        spawn_util_mesh_layout.addRow(self.spawn_cubes_btn)
        spawn_util_mesh_layout.addRow(self.delete_util_meshes_btn)

        spawn_joint_layout = QtWidgets.QFormLayout()
        spawn_joint_layout.addRow(self.spawn_rivet_joint_btn)
        spawn_joint_layout.addRow(self.spawn_center_mesh_joint_btn)

        spawn_curve_controls_grp = QtWidgets.QGroupBox("Curve Controls")
        spawn_curve_controls_grp.setLayout(spawn_curve_controls_layout)
        spawn_util_mesh_grp = QtWidgets.QGroupBox("Utility Meshes")
        spawn_util_mesh_grp.setLayout(spawn_util_mesh_layout)
        spawn_joint_grp = QtWidgets.QGroupBox("Joints")
        spawn_joint_grp.setLayout(spawn_joint_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(spawn_curve_controls_grp)
        main_layout.addWidget(spawn_util_mesh_grp)
        main_layout.addWidget(spawn_joint_grp)
        main_layout.addStretch()

    def create_connections(self):
        """Connect button clicks to actions."""
        self.spawn_spine_controls_btn.clicked.connect(lambda:self.spawn_fk_controls('spine'))
        self.spawn_arm_controls_btn.clicked.connect(lambda:self.spawn_fk_controls('arm'))
        self.spawn_finger_controls_btn.clicked.connect(lambda:self.spawn_fk_controls('finger'))
        self.spawn_cubes_btn.clicked.connect(self.spawn_utility_meshes)
        self.delete_util_meshes_btn.clicked.connect(self.delete_utility_meshes)
        self.spawn_rivet_joint_btn.clicked.connect(self.spawn_rivet_joint)
        self.spawn_center_mesh_joint_btn.clicked.connect(self.spawn_joint_on_pivot)

    def spawn_fk_controls(self, curve_selection=None):
        """Spawns FK controls on selected joints."""

        # Setup
        if self.spawn_target_fk_hierarchy_rb.isChecked():
            selected_joints = JointHelper.get_joints(hierarchy=True)
        else:
            selected_joints = JointHelper.get_joints()

        # Error Handling
        if not selected_joints:
            om.MGlobal.displayWarning("Please select one or more joints to spawn controls on.")
            return
        try:
            if not selected_joints[0].endswith("_jnt"):
                raise ValueError
        except ValueError:
            om.MGlobal.displayWarning("Please add the correct suffixes to your joints.")
            return

        cmds.undoInfo(openChunk=True)
        # Main Functionality
        temp_curve_name = None
        for num, joint in enumerate(selected_joints):
            # Skip tip joints
            if "Tip" in joint:
                break

            # Iterate through joints to create controls
            curve_node_name = joint[:-4] + "_ctl"
            transform_node_name = joint[:-4] + "_grp"
            if curve_selection == 'spine':
                curve_shape = spine_fk_curve(curve_node_name)
                cmds.group(curve_shape, name=transform_node_name)
                cmds.xform(transform_node_name,
                           worldSpace=True,
                           absolute=True,
                           rotatePivot=(0, 0, 0),
                           scalePivot=(0, 0, 0))
            elif curve_selection == 'arm':
                curve_shape = arm_fk_curve(curve_node_name)
                cmds.group(curve_shape, name=transform_node_name)
                cmds.xform(transform_node_name,
                           worldSpace=True,
                           absolute=True,
                           rotatePivot=(0, 0, 0),
                           scalePivot=(0, 0, 0))
            elif curve_selection == 'finger':
                curve_shape = finger_fk_curve(curve_node_name)
                cmds.group(curve_shape, name=transform_node_name)
                cmds.xform(transform_node_name,
                           worldSpace=True,
                           absolute=True,
                           rotatePivot=(0, 0, 0),
                           scalePivot=(0, 0, 0))

            # Skip the root transform from parenting, parent if transform is a child
            if num == 0:
                pass
            else:
                cmds.parent(transform_node_name, temp_curve_name)

            # Store the last curve node name for parenting
            temp_curve_name = curve_node_name

            # Cleanup
            cmds.delete(cmds.parentConstraint(joint, transform_node_name))
            cmds.parentConstraint(curve_node_name, joint)
            cmds.setAttr(f"{curve_node_name}.tx", keyable=False, channelBox=False)
            cmds.setAttr(f"{curve_node_name}.ty", keyable=False, channelBox=False)
            cmds.setAttr(f"{curve_node_name}.tz", keyable=False, channelBox=False)
            cmds.setAttr(f"{curve_node_name}.sx", keyable=False, channelBox=False)
            cmds.setAttr(f"{curve_node_name}.sy", keyable=False, channelBox=False)
            cmds.setAttr(f"{curve_node_name}.sz", keyable=False, channelBox=False)
            cmds.setAttr(f"{curve_node_name}.v", keyable=False, channelBox=False)

        cmds.undoInfo(closeChunk=True)



    def spawn_ik_controls(self, curve_file_name=None):
        """Spawns IK controls on selected joints."""
        pass

    def spawn_utility_meshes(self):
        """Spawns Utility Mesh on selected joints."""

        # Setup
        if self.spawn_target_util_mesh_hierarchy_rb.isChecked():
            selected_joints = JointHelper.get_joints(hierarchy=True)
        else:
            selected_joints = JointHelper.get_joints()

        # Error Handling
        if not selected_joints:
            om.MGlobal.displayWarning("Please select one or more joints to spawn controls on.")
            return
        try:
            if not selected_joints[0].endswith("_jnt"):
                raise ValueError
        except ValueError:
            om.MGlobal.displayWarning("Please add the correct suffixes to your joints.")
            return


        cmds.undoInfo(openChunk=True)
        # Main Functionality
        mesh_list = []
        for joint in selected_joints:
            # Iterate through joints and spawn controls
            mesh = joint[:-4] + "cube_tmp"
            cmds.polyCube(name=mesh, depth=10, width=5, height=5)
            cmds.delete(cmds.parentConstraint(joint, mesh))
            cmds.skinCluster(joint, mesh,
                             toSelectedBones=True,
                             bindMethod=0,
                             normalizeWeights=1,
                             weightDistribution=0,
                             maximumInfluences=1)

            mesh_list.append(mesh)

        # Cleanup
        if not "temp" in cmds.ls():
            cmds.group(mesh_list, name="temp")
        else:
            cmds.parent(mesh_list, "temp")
        cmds.undoInfo(closeChunk=True)

    @staticmethod
    def delete_utility_meshes():
        cmds.delete("temp")

    @staticmethod
    def spawn_rivet_joint():
        """Spawn joint between two selected vertices with a correct orientation."""
        selection = cmds.ls(selection=True, flatten=True)
        if not selection:
            om.MGlobal.displayWarning("Please select 2 vertices.")
            return

        cmds.undoInfo(openChunk=True)
        cmds.Rivet()
        loc = cmds.spaceLocator()[0]
        cmds.delete(cmds.parentConstraint(("pinOutput", "pinOutput1", loc), skipRotate='none'))
        cmds.delete(cmds.orientConstraint('pinOutput', loc))
        cmds.joint()
        cmds.Unparent()
        cmds.delete('pinOutput', 'pinOutput1', loc)
        cmds.undoInfo(closeChunk=True)

    @staticmethod
    def spawn_joint_on_pivot():
        """Spawn joint on the selected transform node's pivot."""
        selection = cmds.ls(selection=True, type='transform')
        if not selection:
            om.MGlobal.displayWarning("Please select 1 object.")
            return

        cmds.undoInfo(openChunk=True)
        joint = cmds.joint()
        cmds.delete(cmds.parentConstraint(selection[0], joint))
        cmds.Unparent()
        cmds.undoInfo(closeChunk=True)

if __name__ == '__main__':
    workspace_control_name = f"{SpawnerWidget.OBJECT_NAME}WorkspaceControl"

    if cmds.workspaceControl(workspace_control_name, exists=True):
        cmds.workspaceControl(workspace_control_name, edit=True, close=True)
        cmds.deleteUI(workspace_control_name)

    window = SpawnerWidget()
    window.show(dockable=True)