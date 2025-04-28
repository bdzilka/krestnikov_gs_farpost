import random
import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="farpost"
)
cursor = conn.cursor()

users = []
NUM_USERS = 10  # количество зарегистрированных пользователей
DATE = datetime.now().date()


def create_users():
    global users
    for i in range(NUM_USERS):
        username = f'user_{i}'
        email = f'user_{i}@mail.com'
        password_hash = 'fakehash'
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, DATE)
        )
        users.append(cursor.lastrowid)
    conn.commit()


def log_action(user_id, action_type, target_id=None, target_type='none', status='success', message=''):
    cursor.execute(
        "INSERT INTO logs (user_id, action_type, target_id, target_type, status, message, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (user_id, action_type, target_id, target_type, status, message, datetime.now())
    )


def create_threads():
    thread_ids = []
    for _ in range(5):
        # 2 раза сделаем ошибки
        if random.random() < 0.4:
            log_action(None, 'create_thread', None, 'thread', 'error', 'User not logged in')
        else:
            user_id = random.choice(users)
            cursor.execute(
                "INSERT INTO threads (title, creator_id, created_at) VALUES (%s, %s, %s)",
                (f'Thread {random.randint(100,999)}', user_id, DATE)
            )
            thread_id = cursor.lastrowid
            thread_ids.append(thread_id)
            log_action(user_id, 'create_thread', thread_id, 'thread')
    conn.commit()
    return thread_ids


def post_messages(thread_ids):
    for _ in range(10):
        if random.random() < 0.5:
            user_id = random.choice(users)
        else:
            user_id = None
        thread_id = random.choice(thread_ids)
        cursor.execute(
            "INSERT INTO messages (thread_id, author_id, content, created_at) VALUES (%s, %s, %s, %s)",
            (thread_id, user_id, f"Random message {random.randint(1000,9999)}", DATE)
        )
        message_id = cursor.lastrowid
        log_action(user_id, 'post_message', message_id, 'message')
    conn.commit()


def simulate_day():
    actions = ['first_visit', 'register', 'login', 'logout', 'visit_thread']
    thread_ids = create_threads()
    post_messages(thread_ids)

    for action in actions:
        for _ in range(5):
            user_id = random.choice(users) if action != 'first_visit' else None
            log_action(user_id, action)


create_users()
simulate_day()

cursor.close()
conn.close()
