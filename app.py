# Attendance management system

# teacher login
# teacher can view the attendance of all the students
# teacher can mark the attendance of the students


# teacher will login and his data will be stored in a database
# create new teacher and show password at the startup
# teacher can login with his username and password

# mark student attendance using json passed
# return the attendance of the student

from flask import Flask, request, jsonify
import sqlite3
import uuid
import logging


temp_cache = {}

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/login', methods=['POST'])
def login():
    try:
        # verify user and password with database
        # if verified then return auth token

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        conn = get_db_connection()
        user_data = conn.execute("SELECT * FROM teacher where name = ? and password = ?;", (username, password)).fetchone()
        conn.close()

        if user_data:
            auth_token = uuid.uuid4()
            # store this in the session to access it afterwards
            temp_cache[username] = auth_token
            logger.info(f"User {username} logged in successfully and auth token is {auth_token}")
            return jsonify({'auth_token': auth_token}), 200
        

        logger.info(f"User {username} login failed")
        return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        logger.error(f"Exception in login api: {e}")
        print(f"Exception while logging in: {e}")
        return jsonify({'error': 'Error while logging in'}), 500


@app.route('/logout', methods=['POST'])
def logout():
    try:
        # remove the auth token from the session
        data = request.get_json()
        username = data.get('username')
        auth_token = data.get('auth_token')

        if temp_cache.get(username) == auth_token:
            del temp_cache[username]
            return jsonify({'message': 'Logged out successfully'}), 200

        return jsonify({'error': 'Invalid username or auth token'}), 401
    
    except Exception as e:
        logger.error(f"Exception: {e}")
        print(f"Exception while logging out: {e}")
        return jsonify({'error': 'Error while logging out'}), 500


@app.route('/attendance', methods=['POST'])
def mark_attendance_multiple():
    # mark attendance for multiple students
    # return the attendance of the student
    try:
        data = request.get_json()
        username = data.get('username')
        auth_token = data.get('auth_token')
        students = data.get('students')
        course_id = data.get('course_id')

        print(temp_cache.get(username))
        print(auth_token)
        print(type(temp_cache.get(username)), type(auth_token))

        if str(temp_cache.get(username)) == auth_token:
            conn = get_db_connection()

            for student in students:
                conn.execute("INSERT INTO attendance (student_id, present, course_id, submitted_by) VALUES (?, ?, ?, ?)", (student['student_id'], student['attendance'], course_id, username))

            conn.commit()
            conn.close()

            return jsonify({'message': 'Attendance marked successfully'}), 200

        return jsonify({'error': 'Invalid username or auth token'}), 401
    
    except Exception as e:
        logger.error(f"Exception: {e}")
        print(f"Exception while marking attendance: {e}")
        return jsonify({'error': 'Error while marking attendance'}), 500
    

@app.route('/attendance/<student_id>', methods=['GET'])
def get_attendance(student_id):
    # get attendance for a student
    

    try:
        # verify the auth token
        auth_token = request.args.get('auth_token')
        username = request.args.get('username')

        if str(temp_cache.get(username)) == str(auth_token):


            conn = get_db_connection()
            attendance_data = conn.execute("SELECT * FROM attendance where student_id = ?;", (student_id,)).fetchall()
            conn.close()

            return jsonify({'attendance': [dict(row) for row in attendance_data]}), 200
        
        return jsonify({'error': 'Invalid username or auth token'}), 401

    except Exception as e:
        logger.error(f"Exception: {e}")
        print(f"Exception while getting attendance: {e}")
        return jsonify({'error': 'Error while getting attendance'}), 500
    


@app.route('/attendance', methods=['GET'])
def get_all_attendance():
    # get attendance for all students
    try:
        # verify the auth token
        # how to get auth token from get request
        auth_token = request.args.get('auth_token')
        username = request.args.get('username')

        if str(temp_cache.get(username)) == str(auth_token):


            conn = get_db_connection()
            attendance_data = conn.execute("SELECT * FROM attendance;").fetchall()
            conn.close()

            return jsonify({'attendance': [dict(row) for row in attendance_data]}), 200
        
        return jsonify({'error': 'Invalid username or auth token'}), 401

    except Exception as e:
        logger.error(f"Exception: {e}")
        print(f"Exception while getting attendance: {e}")
        return jsonify({'error': 'Error while getting attendance'}), 500


if __name__ == '__main__':
    from db import init_db
    init_db.run_sql_script()
    logger.info("Database initialized successfully")

    print("Username and Password for the teacher is: ")
    logger.info("Username and Password for the teacher is: ")
    conn = get_db_connection()
    user_data = conn.execute("SELECT * FROM teacher order by created_at limit 1;").fetchone()
    print(f"username: {user_data['name']}")
    print(f"password: {user_data['password']}")

    logger.info(f"username: {user_data['name']}")
    logger.info(f"password: {user_data['password']}")

    conn.close()



    app.run(debug=True)



