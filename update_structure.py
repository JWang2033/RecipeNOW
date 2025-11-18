# update_readme_with_db_structure.py

import pymysql

# DB_CONFIG = {
#     "host": "localhost",
#     "port": 3307,
#     "user": "root",
#     "password": "WYz@Dessert2025",
#     "database": "dessert_pos",
# }

README = "README.md"
TEMP = "README.tmp"
START_MARKER = "<!-- db:start -->"
END_MARKER = "<!-- db:end -->"

# def get_tables(cursor):
#     cursor.execute("SHOW TABLES")
#     result = cursor.fetchall()
#     if not result:
#         return []
#     key = list(result[0].keys())[0]
#     return [row[key] for row in result]


# def describe_table(cursor, table_name):
#     cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
#     return cursor.fetchall()

# def to_markdown(table_name, columns):
#     md = [f"### `{table_name}` 表结构", ""]
#     md.append("| 字段名 | 类型 | 主键 | 可空 | 默认值 | 注释 |")
#     md.append("|--------|------|------|------|--------|------|")
#     for col in columns:
#         name = col['Field']
#         type_ = col['Type']
#         pk = "✅" if col['Key'] == 'PRI' else ""
#         null = "✅" if col['Null'] == 'YES' else "❌"
#         default = col['Default'] if col['Default'] is not None else ""
#         comment = col['Comment'] if col['Comment'] else ""
#         md.append(f"| {name} | {type_} | {pk} | {null} | {default} | {comment} |")
#     return "\n".join(md)

def update_readme(content):
    with open(README, "r") as f:
        lines = f.readlines()

    with open(TEMP, "w") as f:
        in_block = False
        for line in lines:
            if START_MARKER in line:
                f.write(line)
                f.write("\n")  # optional spacing
                f.write(content)
                f.write("\n")
                in_block = True
            elif END_MARKER in line:
                in_block = False
                f.write(line)
            elif not in_block:
                f.write(line)

    # 替换原文件
    import os
    os.replace(TEMP, README)

def main():
    conn = pymysql.connect(**DB_CONFIG, charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    tables = get_tables(cursor)
    combined_markdown = "\n\n---\n\n".join(
        to_markdown(table, describe_table(cursor, table)) for table in tables
    )

    update_readme(combined_markdown)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
