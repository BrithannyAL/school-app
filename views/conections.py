import mysql.connector
from mysql.connector import Error
import datetime


def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            user='uaq0ezqohaffs987',
            password='C44TvDjOpsgr6cYj6lLU',
            host='bzlw43r4bjaconcjwukt-mysql.services.clever-cloud.com',
            database='bzlw43r4bjaconcjwukt',
            port='3306'
        )
    except Error as e:
        print(f"Error: '{e}'")
    return connection

def get_user(id_user):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT CONCAT(user.name, ' ', user.last_name) AS full_name FROM user WHERE id_user = %s", (id_user,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_chats(supervisor_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT teacher.id_teacher, user.name, user.last_name, 
               MAX(messaging.date) as last_date, MAX(messaging.time) as last_time, 
               MAX(messaging.content) as last_message, 
               SUM(CASE WHEN messaging.id_receiver = %s AND messaging.status = 0 THEN 1 ELSE 0 END) as unread_count
        FROM messaging
        JOIN user ON user.id_user = messaging.id_sender OR user.id_user = messaging.id_receiver
        JOIN teacher ON teacher.id_teacher = user.id_user
        WHERE messaging.id_sender = %s OR messaging.id_receiver = %s
        GROUP BY teacher.id_teacher, user.name, user.last_name
        ORDER BY last_date DESC, last_time DESC
    ''', (supervisor_id, supervisor_id, supervisor_id))
    chats = cursor.fetchall()
    print(chats)
    conn.close()
    return chats

def get_chats_teacher(teacher_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT supervisor.id_user as supervisor_id, user.name, user.last_name, 
               MAX(messaging.date) as last_date, MAX(messaging.time) as last_time, 
               MAX(messaging.content) as last_message, 
               SUM(CASE WHEN messaging.id_receiver = %s AND messaging.status = 0 THEN 1 ELSE 0 END) as unread_count
        FROM messaging
        JOIN user ON user.id_user = messaging.id_sender OR user.id_user = messaging.id_receiver
        JOIN supervisor ON supervisor.id_user = user.id_user
        WHERE (messaging.id_sender = %s OR messaging.id_receiver = %s)
        GROUP BY supervisor.id_user, user.name, user.last_name
        ORDER BY last_date DESC, last_time DESC
    ''', (teacher_id, teacher_id, teacher_id))
    chats = cursor.fetchall()
    print(chats)
    conn.close()
    return chats


def get_messages(supervisor_id, teacher_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT messaging.id_sender, messaging.id_receiver, messaging.content, messaging.date, messaging.time
        FROM messaging
        WHERE (messaging.id_sender = %s AND messaging.id_receiver = %s) OR (messaging.id_sender = %s AND messaging.id_receiver = %s)
        ORDER BY messaging.date ASC, messaging.time ASC
    ''', (supervisor_id, teacher_id, teacher_id, supervisor_id))
    messages = cursor.fetchall()
    conn.close()
    return messages

def send_message(sender_id, receiver_id, content):
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M:%S')
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messaging (id_sender, id_receiver, content, date, time, status)
        VALUES (%s, %s, %s, %s, %s, 0)
    ''', (sender_id, receiver_id, content, date, time))
    conn.commit()
    conn.close()

def get_available_teachers(supervisor_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT DISTINCT teacher.id_teacher, user.name, user.last_name
        FROM teacher
        JOIN user ON teacher.id_teacher = user.id_user   
        JOIN students_group ON students_group.id_teacher = teacher.id_teacher
        JOIN student ON student.id_group = students_group.id_group
        WHERE student.id_student IN (SELECT id_student FROM supervisor WHERE id_user = %s)
    ''', (supervisor_id,))
    teachers = cursor.fetchall()
    print(teachers)
    conn.close()
    return teachers

def get_available_supervisors(teacher_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT DISTINCT supervisor.id_user as supervisor_id, user.name, user.last_name
        FROM supervisor
        JOIN student ON supervisor.id_student = student.id_student
        JOIN students_group ON student.id_group = students_group.id_group
        JOIN teacher ON students_group.id_teacher = teacher.id_teacher
        JOIN user ON supervisor.id_user = user.id_user
        WHERE teacher.id_teacher = %s
    ''', (teacher_id,))
    supervisors = cursor.fetchall()
    print(supervisors)
    conn.close()
    return supervisors

def delete_chat(supervisor_id, teacher_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM messaging
        WHERE (id_sender = %s AND id_receiver = %s) OR (id_sender = %s AND id_receiver = %s)
    ''', (supervisor_id, teacher_id, teacher_id, supervisor_id))
    conn.commit()
    conn.close()
