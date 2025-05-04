import random
import string
import time
import redis
import json

# подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

while True:
    message = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # генерация сообщения
    message_dict = {'message': message}  # словарь
    message_json = json.dumps(message_dict)  # словарь -> json
    r.lpush('messages', message_json)  # отправка сообщения в редис
    print(f"Sent: {message}")
    
    time.sleep(60)  # ждать 1 минуту
