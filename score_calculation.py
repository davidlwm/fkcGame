from tree_node import TreeNode, find_node_by_id

def calculate_score(node, valid_ids, scores):
    if not node:
        return 0
    left_score = calculate_score(node.left_child, valid_ids, scores) if node.left_child else 0
    right_score = calculate_score(node.right_child, valid_ids, scores) if node.right_child else 0
    node_score = 1 if node.node_id in valid_ids and node.left_child and node.right_child else 0
    total_score = node_score + left_score + right_score
    if node.node_id in valid_ids:
        scores[node.node_id] = scores.get(node.node_id, 0) + node_score
    return total_score
