import pymysql
from database_operations import load_tree_data, update_node_scores
from tree_node import TreeNode, build_tree, find_potential_positions
from score_calculation import calculate_score
from strategy_simulation import simulate_add_node_and_calculate, find_optimal_addition_strategy


# 假设已经定义了这些函数或从其他文件中导入
def main():
    # 数据库连接配置
    db_config = {
        'host': '139.159.182.45',
        'user': 'root',
        'password': '123456',
        'database': 'fkc',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    # 加载树数据
    tree_data = load_tree_data(**db_config)
    # 构建树
    root = build_tree(tree_data)
    # 加载有效ID
    valid_ids = load_valid_ids('valid_ids.txt')

    # 初始化分数字典
    scores = {}
    # 计算初始积分
    calculate_score(root, valid_ids, scores)

    # 更新数据库中的节点积分
    connection = pymysql.connect(**db_config)
    try:
        update_node_scores(connection, scores)
    finally:
        connection.close()

    # 示例：试算在特定位置添加节点后的积分变化
    # 假设 node_id_to_add 是想要添加节点的父节点ID
    node_id_to_add = 'some_node_id'
    simulate_add_node_and_calculate(root, node_id_to_add, valid_ids, scores)

    # 示例：找出添加多个节点的最优策略
    num_nodes_to_add = 5
    optimal_positions = find_optimal_addition_strategy(root, valid_ids, num_nodes_to_add)
    print(f"Optimal positions to add {num_nodes_to_add} nodes: {optimal_positions}")


def load_valid_ids_from_db(connection, prefix):
    valid_ids = set()
    try:
        with connection.cursor() as cursor:
            # 选择具有特定前缀的 node_id
            sql = "SELECT node_id FROM BinaryTree WHERE node_id LIKE %s"
            cursor.execute(sql, (prefix + '%',))
            result = cursor.fetchall()
            for row in result:
                valid_ids.add(row['node_id'])
    except Exception as e:
        print(f"Error loading valid IDs from database: {e}")
    return valid_ids

def load_valid_ids_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return set()

def load_valid_ids(connection, prefix='prefix_', file_path=None):
    valid_ids = load_valid_ids_from_db(connection, prefix)
    if file_path:
        valid_ids.update(load_valid_ids_from_file(file_path))
    return valid_ids



if __name__ == "__main__":
    main()
