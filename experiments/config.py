excluded_joints = ["LeftHandIndex1", "LeftHandIndex2", "LeftHandIndex3", "LeftHandMiddle1", "LeftHandMiddle2", "LeftHandMiddle3", "LeftHandPinky1", "LeftHandPinky2", "LeftHandPinky3", "LeftHandRing1", "LeftHandRing2", "LeftHandRing3", "LeftHandThumb1", "LeftHandThumb2", "LeftHandThumb3", "RightHandIndex1", "RightHandIndex2", "RightHandIndex3", "RightHandMiddle1", "RightHandMiddle2", "RightHandMiddle3", "RightHandPinky1", "RightHandPinky2", "RightHandPinky3", "RightHandRing1", "RightHandRing2", "RightHandRing3", "RightHandThumb1", "RightHandThumb2", "RightHandThumb3"]

joints_config = {

    # CNS

    # Hips Spine LVecBase3f(1, 4.68006, 1) LVecBase3f(1, 8.12742, 1)
    # Hips LeftUpLeg LVecBase3f(1, 4.68006, 1) LVecBase3f(1, 20.8829, 1)
    # Hips RightUpLeg LVecBase3f(1, 4.68006, 1) LVecBase3f(1, 20.8829, 1)

    "Hips": {
        "mass": 0,
        "joints": {
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

    # Left Leg

    "LeftUpLeg": {
        "mass": 10,
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
        "mass": 10,
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
        "joints": {
            "LeftToeBase": {
                "type": None
            }
        }
    },

    # Right Leg

    "RightUpLeg": {
        "mass": 10,
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
        "mass": 10,
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
        "joints": {
            "RightToeBase": {
                "type": None
            }
        }
    }
}
