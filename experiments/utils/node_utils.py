def rotate_node(node, dq):
    q = node.getQuat()
    node.setQuat(q * dq)
