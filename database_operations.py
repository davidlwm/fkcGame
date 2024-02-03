import pymysql.cursors

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

def update_node_scores(connection, scores):
    with connection.cursor() as cursor:
        for node_id, score in scores.items():
            cursor.execute("SELECT node_id FROM NodeScores WHERE node_id = %s", (node_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE NodeScores SET score = %s WHERE node_id = %s", (score, node_id))
            else:
                cursor.execute("INSERT INTO NodeScores (node_id, score) VALUES (%s, %s)", (node_id, score))
        connection.commit()
