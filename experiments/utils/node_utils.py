def rotate_node(node, dq):
    q = node.get_quat()
    node.set_quat(q * dq)
