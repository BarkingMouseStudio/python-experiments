excluded_joints = ["LeftHandIndex1", "LeftHandIndex2", "LeftHandIndex3", "LeftHandMiddle1", "LeftHandMiddle2", "LeftHandMiddle3", "LeftHandPinky1", "LeftHandPinky2", "LeftHandPinky3", "LeftHandRing1", "LeftHandRing2", "LeftHandRing3", "LeftHandThumb1", "LeftHandThumb2", "LeftHandThumb3", "RightHandIndex1", "RightHandIndex2", "RightHandIndex3", "RightHandMiddle1", "RightHandMiddle2", "RightHandMiddle3", "RightHandPinky1", "RightHandPinky2", "RightHandPinky3", "RightHandRing1", "RightHandRing2", "RightHandRing3", "RightHandThumb1", "RightHandThumb2", "RightHandThumb3"]

center_joints = {
    "Spine": 1 + 4 + 4,
    "Spine1": 1,
    "Spine2": 1 + 4 + 4,
    "Neck": 1,
    "Neck1": 1,
    "Head": 1
}

joints_config = {

  # CNS

  "Spine": {
    "mass": 1,
    "joints": {
        "Spine1": {},
        "LeftUpLeg": {
            "offset_parent": (0, -1, 0),
            "offset_child": (0, -1, 0),
        },
        "RightUpLeg": {
            "offset_parent": (0, -1, 0),
            "offset_child": (0, -1, 0),
        },
    }
  },

  "Spine1": {
    "mass": 1,
    "joints": {
        "Spine2": {}
    }
  },

  "Spine2": {
    "mass": 1,
    "joints": {
        "Neck": {},
        "LeftShoulder": {},
        "RightShoulder": {},
    }
  },

  "Neck": {
    "mass": 1,
    "joints": {
        "Neck1": {}
    }
  },

  "Neck1": {
    "mass": 1,
    "joints": {
        "Head": {}
    }
  },

  # Left Leg

  "LeftUpLeg": {
    "mass": 1,
    "joints": {
        "LeftLeg": {}
    }
  },
  "LeftLeg": {
    "mass": 1,
    "joints": {
        "LeftFoot": {}
    }
  },
  "LeftFoot": {
    "mass": 1,
    "joints": {
        "LeftToeBase": {}
    }
  },

  # Right Leg

  "RightUpLeg": {
    "mass": 1,
    "joints": {
        "RightLeg": {}
    }
  },
  "RightLeg": {
    "mass": 1,
    "joints": {
        "RightFoot": {}
    }
  },
  "RightFoot": {
    "mass": 1,
    "joints": {
        "RightToeBase": {}
    }
  },

  # Left Arm

  "LeftShoulder": {
    "mass": 1,
    "joints": {
        "LeftArm": {}
    }
  },
  "LeftArm": {
    "mass": 1,
    "joints": {
        "LeftForeArm": {}
    }
  },
  "LeftForeArm": {
    "mass": 1,
    "joints": {
        "LeftHand": {}
    }
  },

  # Right Arm

  "RightShoulder": {
    "mass": 1,
    "joints": {
        "RightArm": {}
    }
  },
  "RightArm": {
    "mass": 1,
    "joints": {
        "RightForeArm": {}
    }
  },
  "RightForeArm": {
    "mass": 1,
    "joints": {
        "RightHand": {}
    }
  },

  # Extremities

  "LeftToeBase": {
    "mass": 1,
  },
  "RightToeBase": {
    "mass": 1,
  },

  "LeftHand": {
    "mass": 1,
  },
  "RightHand": {
    "mass": 1,
  },

  "Head": {
    "mass": 1,
  },
}
