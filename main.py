import pymysql.cursors

class TreeNode:
    def __init__(self, node_id, left_child=None, right_child=None, parent_node=None):
        self.node_id = node_id
        self.left_child = left_child
        self.right_child = right_child
        self.parent_node = parent_node

def load_tree_data():
    connection = pymysql.connect(host='your_host',
                                 user='your_user',
                                 password='your_password',
                                 database='your_database',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT node_id, left_child, right_child, parent_node FROM BinaryTree"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

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

def load_valid_ids(file_path):
    with open(file_path, 'r') as file:
        return set(line.strip() for line in file.readlines())

# CREATE TABLE `NodeScores` (
#   `node_id` varchar(16) NOT NULL,
#   `score` int NOT NULL,
#   `last_update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#   PRIMARY KEY (`node_id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



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

def update_node_scores(connection, scores):
    with connection.cursor() as cursor:
        for node_id, score in scores.items():
            # 检查节点是否已存在
            cursor.execute("SELECT node_id FROM NodeScores WHERE node_id = %s", (node_id,))
            if cursor.fetchone():
                # 更新现有记录
                cursor.execute("UPDATE NodeScores SET score = %s WHERE node_id = %s", (score, node_id))
            else:
                # 插入新记录
                cursor.execute("INSERT INTO NodeScores (node_id, score) VALUES (%s, %s)", (node_id, score))
        connection.commit()

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

def simulate_add_and_calculate(root, add_positions, valid_ids):
    original_scores = {}  # 用于存储原始积分
    calculate_score(root, valid_ids, original_scores)  # 计算原始积分

    max_increase = 0
    best_position = None
    for position in add_positions:
        node = find_node_by_id(root, position[0])
        if node:
            # 模拟添加节点
            if position[1] == 'left' and not node.left_child:
                node.left_child = TreeNode("temp")
            elif position[1] == 'right' and not node.right_child:
                node.right_child = TreeNode("temp")
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


def simulate_add_node_and_calculate_score(root, node_id_to_add, valid_ids, scores):
    node_to_add = find_node_by_id(root, node_id_to_add)
    if not node_to_add:
        print(f"No node found with ID: {node_id_to_add}")
        return

    # 假设添加左子节点（如果左子节点存在，则添加右子节点）
    if not node_to_add.left_child:
        node_to_add.left_child = TreeNode("temp_left")
    elif not node_to_add.right_child:
        node_to_add.right_child = TreeNode("temp_right")
    else:
        print("Both child nodes are already present. Cannot add more nodes here.")
        return

    # 重新计算分数
    scores = {}
    new_score = calculate_score(root, valid_ids, scores)
    print(f"New total score after adding node: {new_score}")

    # 移除添加的节点，恢复原始状态
    if node_to_add.left_child and node_to_add.left_child.node_id == "temp_left":
        node_to_add.left_child = None
    if node_to_add.right_child and node_to_add.right_child.node_id == "temp_right":
        node_to_add.right_child = None

def find_potential_positions(node, potential_positions, node_id=None):
    if node is None:
        return

    # 如果当前节点有左子节点，递归检查左子树
    if node.left_child is not None:
        find_potential_positions(node.left_child, potential_positions, node.node_id)
    else:
        # 如果没有左子节点，记录这个作为潜在添加位置
        potential_positions.append((node.node_id, 'left'))

    # 如果当前节点有右子节点，递归检查右子树
    if node.right_child is not None:
        find_potential_positions(node.right_child, potential_positions, node.node_id)
    else:
        # 如果没有右子节点，记录这个作为潜在添加位置
        potential_positions.append((node.node_id, 'right'))


def find_optimal_addition_strategy(root, valid_ids, num_nodes_to_add):
    add_positions = []  # 初始化添加位置列表
    for _ in range(num_nodes_to_add):
        # 获取当前所有可能的添加位置
        potential_positions = []
        find_potential_positions(root, potential_positions)
        # 计算每个潜在位置的最佳添加策略
        best_position, increase = simulate_add_and_calculate(root, potential_positions, valid_ids)
        if best_position:
            add_positions.append(best_position)
            # 实际添加节点以更新树的状态
            node = find_node_by_id(root, best_position[0])
            if best_position[1] == 'left':
                node.left_child = TreeNode("temp")
            else:
                node.right_child = TreeNode("temp")
        else:
            break  # 如果没有找到合适的位置，则停止

    return add_positions


def main():
    # Load data from database
    data = load_tree_data()
    # Build the binary tree
    root = build_tree(data)
    # Load valid node IDs from file
    valid_ids = load_valid_ids('valid_ids.txt')
    # Initialize a dictionary to store scores
    scores = {}
    # Calculate the score
    calculate_score(root, valid_ids, scores)
    print(f"Scores: {scores}")
    # Update database with node scores
    connection = pymysql.connect(host='your_host',
                                 user='your_user',
                                 password='your_password',
                                 database='your_database',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        update_node_scores(connection, scores)
    finally:
        connection.close()


if __name__ == "__main__":
    main()

