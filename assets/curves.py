import maya.cmds as cmds

SPINE_FK_POINTS = [[-0.0, 0.0, 0.0],
                   [-0.0, 9.496, 0.0],
                   [0.0, 12.661, -3.165],
                   [0.0, 15.827, -3.165],
                   [-0.0, 15.827, 3.165],
                   [-0.0, 12.661, 3.165],
                   [-0.0, 9.496, 0.0]]

FINGER_FK_POINTS = [[0.0, 1.664, -1.069],
                   [0.0, 2.354, 0.0],
                   [0.0, 1.664, 1.069],
                   [0.0, -0.0, 1.512],
                   [0.0, -1.664, 1.069],
                   [0.0, -2.354, 0.0],
                   [0.0, -1.664, -1.069],
                   [0.0, -0.0, -1.512],
                   [0.0, 1.664, -1.069],
                   [0.0, 2.354, 0.0],
                   [0.0, 1.664, 1.069]]


def spine_fk_curve(curve_node_name):
    curve_shape = cmds.curve(point=SPINE_FK_POINTS,
                             degree=1,
                             name=curve_node_name)
    return curve_shape

def arm_fk_curve(curve_node_name):
    curve_shape = cmds.circle(center=(0, 0, 0),
                                          normal=(1, 0, 0),
                                          sweep=360,
                                          radius=6,
                                          degree=3,
                                          useTolerance=False,
                                          tolerance=0.01,
                                          sections=8,
                                          constructionHistory=True,
                                          name=curve_node_name)[0]
    return curve_shape

def finger_fk_curve(curve_node_name):
    curve_shape = cmds.curve(point=FINGER_FK_POINTS,
                             degree=3,
                             periodic=2,
                             knot=[-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
                             name=curve_node_name)
    return curve_shape





