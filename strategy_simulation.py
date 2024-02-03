from tree_node import TreeNode, find_node_by_id, find_potential_positions
from score_calculation import calculate_score

def simulate_add_node_and_calculate(root, add_positions, valid_ids):
    original_scores = {}  # 用于存储原始积分
    calculate_score(root, valid_ids, original_scores)  # 计算原始积分

    max_increase = 0
    best_position = None
    for position in add_positions:
        node = find_node_by_id(root, position[0])
        if node:
            # 模拟添加节点
            temp_node = TreeNode("temp")
            if position[1] == 'left' and not node.left_child:
                node.left_child = temp_node
            elif position[1] == 'right' and not node.right_child:
                node.right_child = temp_node
            else:
                continue  # 如果指定位置已有子节点，则跳过

            # 计算添加后的积分
            new_scores = {}
            new_score = calculate_score(root, valid_ids, new_scores)
            increase = new_score - sum(original_scores.values())  # 计算积分增加

            # 检查是否是最大增加
            if increase > max_increase:
                max_increase = increase
                best_position = position

            # 撤销添加
            if position[1] == 'left':
                node.left_child = None
            else:
                node.right_child = None

    return best_position, max_increase

def find_optimal_addition_strategy(root, valid_ids, num_nodes_to_add):
    add_positions = []  # 初始化添加位置列表
    for _ in range(num_nodes_to_add):
        # 获取当前所有可能的添加位置
        potential_positions = []
        find_potential_positions(root, potential_positions)
        # 计算每个潜在位置的最佳添加策略
        best_position, increase = simulate_add_node_and_calculate(root, potential_positions, valid_ids)
        if best_position:
            add_positions.append(best_position)
            # 实际添加节点以更新树的状态
            node = find_node_by_id(root, best_position[0])
            temp_node = TreeNode("temp")
            if best_position[1] == 'left':
                node.left_child = temp_node
            else:
                node.right_child = temp_node
        else:
            break  # 如果没有找到合适的位置，则停止

    return add_positions
