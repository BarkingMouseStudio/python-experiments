excluded_joints = ["LeftHandIndex1", "LeftHandIndex2", "LeftHandIndex3", "LeftHandMiddle1", "LeftHandMiddle2", "LeftHandMiddle3", "LeftHandPinky1", "LeftHandPinky2", "LeftHandPinky3", "LeftHandRing1", "LeftHandRing2", "LeftHandRing3", "LeftHandThumb1", "LeftHandThumb2", "LeftHandThumb3", "RightHandIndex1", "RightHandIndex2", "RightHandIndex3", "RightHandMiddle1", "RightHandMiddle2", "RightHandMiddle3", "RightHandPinky1", "RightHandPinky2", "RightHandPinky3", "RightHandRing1", "RightHandRing2", "RightHandRing3", "RightHandThumb1", "RightHandThumb2", "RightHandThumb3"]

joints_config = {

  # CNS

  "Spine": {
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
    "joints": {
        "Spine2": {}
    }
  },

  "Spine2": {
    "joints": {
        "Neck": {},
        "LeftShoulder": {},
        "RightShoulder": {},
    }
  },

  "Neck": {
    "joints": {
        "Neck1": {}
    }
  },

  "Neck1": {
    "joints": {
        "Head": {}
    }
  },

  # Left Leg

  "LeftUpLeg": {
    "joints": {
        "LeftLeg": {}
    }
  },
  "LeftLeg": {
    "joints": {
        "LeftFoot": {}
    }
  },
  "LeftFoot": {
    "joints": {
        "LeftToeBase": {}
    }
  },

  # Right Leg

  "RightUpLeg": {
    "joints": {
        "RightLeg": {}
    }
  },
  "RightLeg": {
    "joints": {
        "RightFoot": {}
    }
  },
  "RightFoot": {
    "joints": {
        "RightToeBase": {}
    }
  },

  # Left Arm

  "LeftShoulder": {
    "joints": {
        "LeftArm": {}
    }
  },
  "LeftArm": {
    "joints": {
        "LeftForeArm": {}
    }
  },
  "LeftForeArm": {
    "joints": {
        "LeftHand": {}
    }
  },

  # Right Arm

  "RightShoulder": {
    "joints": {
        "RightArm": {}
    }
  },
  "RightArm": {
    "joints": {
        "RightForeArm": {}
    }
  },
  "RightForeArm": {
    "joints": {
        "RightHand": {}
    }
  },

  # Extremities

  "LeftToeBase": {},
  "RightToeBase": {},

  "LeftHand": {},
  "RightHand": {},

  "Head": {},
}
