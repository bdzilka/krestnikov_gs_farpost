import csv
import mysql.connector
from datetime import datetime, timedelta


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="farpost"
)
cursor = conn.cursor(dictionary=True)


def aggregate(start_date, end_date, output_file):
    day = start_date
    previous_total_threads = 0

    with open(output_file, mode='w', newline='') as csvfile:
        fieldnames = [
            'day', 'new_accounts', 'anonymous_message_percent',
            'total_messages', 'threads_change_percent'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()

        while day <= end_date:
            next_day = day + timedelta(days=1)

            # новые аккаунты
            cursor.execute(
                "SELECT COUNT(*) as count FROM users WHERE created_at >= %s AND created_at < %s",
                (day, next_day)
            )
            new_accounts = cursor.fetchone()['count']

            # сообщения
            cursor.execute(
                "SELECT COUNT(*) as total FROM messages WHERE created_at >= %s AND created_at < %s",
                (day, next_day)
            )
            total_messages = cursor.fetchone()['total']

            cursor.execute(
                "SELECT COUNT(*) as anonymous FROM messages WHERE created_at >= %s AND created_at < %s "
                "AND author_id IS NULL",
                (day, next_day)
            )
            anonymous_messages = cursor.fetchone()['anonymous']

            anonymous_percent = (anonymous_messages / total_messages) * 100 if total_messages else 0

            # темы
            cursor.execute(
                "SELECT COUNT(*) as total_threads FROM threads WHERE created_at <= %s "
                "AND (deleted_at IS NULL OR deleted_at > %s)",
                (next_day, day)
            )
            total_threads = cursor.fetchone()['total_threads']

            threads_change_percent = 0
            if previous_total_threads > 0:
                threads_change_percent = ((total_threads - previous_total_threads) / previous_total_threads) * 100

            previous_total_threads = total_threads

            writer.writerow({
                'day': day.strftime('%Y-%m-%d'),
                'new_accounts': new_accounts,
                'anonymous_message_percent': round(anonymous_percent, 2),
                'total_messages': total_messages,
                'threads_change_percent': round(threads_change_percent, 2)
            })

            day = next_day


# пример запуска:
start = datetime.strptime('2025-04-25', '%Y-%m-%d').date()
end = datetime.strptime('2025-04-29', '%Y-%m-%d').date()
aggregate(start, end, 'forum_aggregation.csv')

cursor.close()
conn.close()
