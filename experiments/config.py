excluded_joints = ["LeftHandIndex1", "LeftHandIndex2", "LeftHandIndex3", "LeftHandMiddle1", "LeftHandMiddle2", "LeftHandMiddle3", "LeftHandPinky1", "LeftHandPinky2", "LeftHandPinky3", "LeftHandRing1", "LeftHandRing2", "LeftHandRing3", "LeftHandThumb1", "LeftHandThumb2", "LeftHandThumb3", "RightHandIndex1", "RightHandIndex2", "RightHandIndex3", "RightHandMiddle1", "RightHandMiddle2", "RightHandMiddle3", "RightHandPinky1", "RightHandPinky2", "RightHandPinky3", "RightHandRing1", "RightHandRing2", "RightHandRing3", "RightHandThumb1", "RightHandThumb2", "RightHandThumb3"]

joints_config = {

    # CNS

    "Hips": {
        "mass": 1,
        "joints": {
            "Spine": {
                "type": "cone",
                "limit": (90, 90, 180),
                "offset_parent": (0, -1, 0),
                "offset_child": (0, -1, 0),
            },
            "LeftUpLeg": {
                "type": "cone",
                "limit": (90, 90, 180),
                "offset_parent": (1, 0, 0),
                "offset_child": (0, -1, 0),
            },
            "RightUpLeg": {
                "type": "cone",
                "limit": (90, 90, 180),
                "offset_parent": (-1, 0, 0),
                "offset_child": (0, -1, 0),
            },
        },
    },

    "Spine": {
        "joints": {
            "Spine1": {
                "type": "cone",
                "limit": (90, 90, 360)
            },
        }
    },

    "Spine1": {
        "joints": {
            "Spine2": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },

    "Spine2": {
        "joints": {
            "Neck": {
                "type": "cone",
                "limit": (90, 90, 360)
            },
            "LeftShoulder": {
                "type": "cone",
                "limit": (90, 90, 360)
            },
            "RightShoulder": {
                "type": "cone",
                "limit": (90, 90, 360)
            },
        }
    },

    "Neck": {
        "joints": {
            "Neck1": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },

    "Neck1": {
        "joints": {
            "Head": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },

    # Left Leg

    "LeftUpLeg": {
        "joints": {
            "LeftLeg": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },
    "LeftLeg": {
        "joints": {
            "LeftFoot": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "limit": (-180, 0)
            }
        }
    },
    "LeftFoot": {
        "joints": {
            "LeftToeBase": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "limit": (45, 135)
            }
        }
    },

    # Right Leg

    "RightUpLeg": {
        "joints": {
            "RightLeg": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },
    "RightLeg": {
        "joints": {
            "RightFoot": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "limit": (-180, 0)
            }
        }
    },
    "RightFoot": {
        "joints": {
            "RightToeBase": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "limit": (45, 135)
            }
        }
    },

    # Left Arm

    "LeftShoulder": {
        "joints": {
            "LeftArm": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },
    "LeftArm": {
        "joints": {
            "LeftForeArm": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },
    "LeftForeArm": {
        "joints": {
            "LeftHand": {
                "type": "hinge",
                "axis_parent": (1, 0, 0),
                "axis_child": (1, 0, 0),
                "limit": (0, 180)
            }
        }
    },

    # Right Arm

    "RightShoulder": {
        "joints": {
            "RightArm": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },
    "RightArm": {
        "joints": {
            "RightForeArm": {
                "type": "cone",
                "limit": (90, 90, 360)
            }
        }
    },
    "RightForeArm": {
        "joints": {
            "RightHand": {
                "type": "hinge",
                "axis_parent": (-1, 0, 0),
                "axis_child": (-1, 0, 0),
                "limit": (0, 180)
            }
        }
    },

    # Extremities

    "LeftToeBase": {},
    "RightToeBase": {},
    "LeftHand": {},
    "RightHand": {},
    "Head": {}
}
