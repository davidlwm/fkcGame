class TreeNode:
    def __init__(self, node_id, left_child=None, right_child=None, parent_node=None):
        self.node_id = node_id
        self.left_child = left_child
        self.right_child = right_child
        self.parent_node = parent_node

def find_node_by_id(node, node_id):
    if not node:
        return None
    if node.node_id == node_id:
        return node
    left_result = find_node_by_id(node.left_child, node_id)
    if left_result:
        return left_result
    right_result = find_node_by_id(node.right_child, node_id)
    return right_result

def build_tree(data):
    nodes = {}
    root = None

    for item in data:
        node_id = item['node_id']
        if node_id not in nodes:
            nodes[node_id] = TreeNode(node_id)
        node = nodes[node_id]

        for child_type in ['left_child', 'right_child']:
            child_id = item[child_type]
            if child_id:
                if child_id not in nodes:
                    nodes[child_id] = TreeNode(child_id)
                setattr(node, child_type, nodes[child_id])
                nodes[child_id].parent_node = node

        if not item['parent_node']:
            root = node

    return root

def find_potential_positions(node, potential_positions):
    if node is None:
        return

    # 如果当前节点有左子节点，递归检查左子树
    if node.left_child is not None:
        find_potential_positions(node.left_child, potential_positions)
    else:
        # 如果没有左子节点，记录这个作为潜在添加位置
        potential_positions.append((node.node_id, 'left'))

    # 如果当前节点有右子节点，递归检查右子树
    if node.right_child is not None:
        find_potential_positions(node.right_child, potential_positions)
    else:
        # 如果没有右子节点，记录这个作为潜在添加位置
        potential_positions.append((node.node_id, 'right'))
