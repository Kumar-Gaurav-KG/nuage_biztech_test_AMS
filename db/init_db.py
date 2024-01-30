import sqlite3
import os

# get current directory

def run_sql_script():
    try:
        schema_dir = os.path.dirname(__file__) + '/schema.sql'
        print(schema_dir)

        connection = sqlite3.connect('database.db')

        with open(schema_dir) as f:
            connection.executescript(f.read())


        cur = connection.cursor()

        cur.execute("""INSERT INTO teacher (name, email, password) VALUES ('teacher1', 'teacher1@gmail.com', 'test@123')""")

        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Exception while running sql script: {e}")
        raise Exception("Error in running sql script")