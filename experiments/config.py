excluded_joints = ["LeftHandIndex1", "LeftHandIndex2", "LeftHandIndex3", "LeftHandMiddle1", "LeftHandMiddle2", "LeftHandMiddle3", "LeftHandPinky1", "LeftHandPinky2", "LeftHandPinky3", "LeftHandRing1", "LeftHandRing2", "LeftHandRing3", "LeftHandThumb1", "LeftHandThumb2", "LeftHandThumb3", "RightHandIndex1", "RightHandIndex2", "RightHandIndex3", "RightHandMiddle1", "RightHandMiddle2", "RightHandMiddle3", "RightHandPinky1", "RightHandPinky2", "RightHandPinky3", "RightHandRing1", "RightHandRing2", "RightHandRing3", "RightHandThumb1", "RightHandThumb2", "RightHandThumb3"]

joints_config = {

    # CNS

    # Hips Spine LVecBase3f(1, 4.68006, 1) LVecBase3f(1, 8.12742, 1)
    # Hips LeftUpLeg LVecBase3f(1, 4.68006, 1) LVecBase3f(1, 20.8829, 1)
    # Hips RightUpLeg LVecBase3f(1, 4.68006, 1) LVecBase3f(1, 20.8829, 1)

    "Hips": {
        "mass": 100,
        "F_max": 0,
        "axis": (1, 0, 0),
        "joints": {
            "Spine": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "offset_parent": (0, 8.75134, -3.32052),
                "offset_child": (0, -8.1274, 0),
            },
            "LeftUpLeg": {
                "type": "hinge",
                "limit": (-200, -90),
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "offset_parent": (9.6338, -2.821, 1.66026),
                "offset_child": (0, -20.8829, 0),
            },
            "RightUpLeg": {
                "type": "hinge",
                "limit": (-200, -90),
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "offset_parent": (-9.6338, -2.821, 1.66026),
                "offset_child": (0, -20.8829, 0),
            },
        },
    },

    "Spine": {
        "mass": 10,
        "F_max": 4000.0,
        "axis": (1, 0, 0),
        "joints": {
            "Spine1": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
            },
        }
    },

    # Spine1 Spine2 LPoint3f(0, 13.7007, 0)
    # Spine1 Spine2 LVecBase3f(1, 6.85034, 1) LVecBase3f(1, 6.2423, 1)

    "Spine1": {
        "mass": 10,
        "F_max": 400.0,
        "axis": (1, 0, 0),
        "joints": {
            "Spine2": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "offset_parent": (0, 6.8503, 0),
                "offset_child": (0, 0, 0),
            }
        }
    },

    # print node.getName(), child_node.getName(), child_node.getPos(child_parent)
    # Spine2 RightShoulder LPoint3f(-6.14139, 10.8672, -0.228481)
    # Spine2 Neck LPoint3f(-0.0016115, 14.5373, 0.45673)
    # Spine2 LeftShoulder LPoint3f(6.14301, 10.8686, -0.228251)


    # print parent.getName(), child.getName(), extents_parent, extents_child
    # Spine2 RightShoulder LVecBase3f(1, 6.2423, 1) LVecBase3f(1, 6.25128, 1)
    # Spine2 Neck LVecBase3f(1, 6.2423, 1) LVecBase3f(1, 2.21894, 1)
    # Spine2 LeftShoulder LVecBase3f(1, 6.2423, 1) LVecBase3f(1, 6.24931, 1)

    "Spine2": {
        "mass": 10,
        "F_max": 200.0,
        "axis": (1, 0, 0),
        "joints": {
            "Neck": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "offset_parent": (-0.0016115, 14.5373, 0.45673),
                "offset_child": (0, -2.2189, 0),
            },
            "LeftShoulder": {
                "type": "hinge",
                "axis_parent": (0, 0, 1),
                "axis_child": (0, 0, 1),
                "offset_parent": (6.14301, 10.8686, -0.228251),
                "offset_child": (0, -6.2493, 0),
            },
            "RightShoulder": {
                "type": "hinge",
                "axis_parent": (0, 0, 1),
                "axis_child": (0, 0, 1),
                "offset_parent": (-6.14139, 10.8672, -0.228481),
                "offset_child": (0, -6.2512, 0),
            },
        }
    },

    "Neck": {
        "mass": 5,
        "F_max": 100.0,
        "axis": (1, 0, 0),
        "joints": {
            "Neck1": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
            }
        }
    },

    "Neck1": {
        "mass": 1,
        "F_max": 0.0,
        "axis": (1, 0, 0),
        "joints": {
            "Head": {
                "type": None
            }
        }
    },

    # Left Leg

    "LeftUpLeg": {
        "mass": 30,
        "F_max": 200000.0,
        "axis": (1, 0, 0),
        "joints": {
            "LeftLeg": {
                "type": "hinge",
                "limit": (-90, 0),
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
            }
        }
    },
    "LeftLeg": {
        "mass": 20,
        "F_max": 40000.0,
        "axis": (1, 0, 0),
        "joints": {
            "LeftFoot": {
                "type": "hinge",
                "limit": (25, 85),
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
            }
        }
    },
    "LeftFoot": {
        "mass": 10,
        "F_max": 4000.0,
        "axis": (1, 0, 0),
        "joints": {
            "LeftToeBase": {
                "type": None
            }
        }
    },

    # Right Leg

    "RightUpLeg": {
        "mass": 30,
        "F_max": 200000.0,
        "axis": (1, 0, 0),
        "joints": {
            "RightLeg": {
                "type": "hinge",
                "limit": (-90, 0),
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
            }
        }
    },
    "RightLeg": {
        "mass": 20,
        "F_max": 40000.0,
        "axis": (1, 0, 0),
        "joints": {
            "RightFoot": {
                "type": "hinge",
                "limit": (25, 85),
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
            }
        }
    },
    "RightFoot": {
        "mass": 10,
        "F_max": 4000.0,
        "axis": (1, 0, 0),
        "joints": {
            "RightToeBase": {
                "type": None
            }
        }
    },

    # Left Arm

    "LeftShoulder": {
        "mass": 20,
        "F_max": 40000.0,
        "axis": (0, 0, 1),
        "joints": {
            "LeftArm": {
                "type": "hinge",
                "axis_parent": (0, 0, 1),
                "axis_child": (0, 0, 1),
            }
        }
    },
    "LeftArm": {
        "mass": 10,
        "F_max": 4000.0,
        "axis": (0, 0, 1),
        "joints": {
            "LeftForeArm": {
                "type": "hinge",
                "axis_parent": (0, 0, 1),
                "axis_child": (0, 0, 1),
            }
        }
    },
    "LeftForeArm": {
        "mass": 5,
        "F_max": 2000.0,
        "axis": (0, 0, 1),
        "joints": {
            "LeftHand": {
                "type": None
            }
        }
    },

    # Right Arm

    "RightShoulder": {
        "mass": 20,
        "F_max": 40000.0,
        "axis": (0, 0, 1),
        "joints": {
            "RightArm": {
                "type": "hinge",
                "axis_parent": (0, 0, 1),
                "axis_child": (0, 0, 1),
            }
        }
    },
    "RightArm": {
        "mass": 10,
        "F_max": 4000.0,
        "axis": (0, 0, 1),
        "joints": {
            "RightForeArm": {
                "type": "hinge",
                "axis_parent": (0, 0, 1),
                "axis_child": (0, 0, 1),
            }
        }
    },
    "RightForeArm": {
        "mass": 5,
        "F_max": 2000.0,
        "axis": (0, 0, 1),
        "joints": {
            "RightHand": {
                "type": None
            }
        }
    }
}
