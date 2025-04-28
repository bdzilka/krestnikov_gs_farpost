import sqlite3
from collections.abc import Collection


class TableData(Collection):
    def __init__(self, database_name, table_name):
        self.database_name = database_name
        self.table_name = table_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.database_name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'conn'):
            self.conn.close()

    def __len__(self):
        # кол-во записей в таблице
        with self as table:
            query = f"SELECT COUNT(*) FROM {self.table_name}"
            table.cursor.execute(query)
            return table.cursor.fetchone()[0]

    def __contains__(self, name):
        # есть ли запись с таким именем в таблице
        with self as table:
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE name = ?"
            table.cursor.execute(query, (name,))
            return table.cursor.fetchone()[0] > 0

    def __getitem__(self, name):
        # одна запись по имени
        with self as table:
            query = f"SELECT * FROM {self.table_name} WHERE name = ?"
            table.cursor.execute(query, (name,))
            row = table.cursor.fetchone()
            if row:
                return dict(zip([column[0] for column in table.cursor.description], row))
            else:
                raise KeyError(f"Name '{name}' not found in table '{self.table_name}'")

    def __iter__(self):
        # итерация по записям в таблице
        with self as table:
            query = f"SELECT * FROM {self.table_name}"
            table.cursor.execute(query)
            columns = [column[0] for column in table.cursor.description]
            for row in table.cursor:
                yield dict(zip(columns, row))

# пример использования:


with TableData(database_name='example.sqlite', table_name='presidents') as presidents:
    # количество записей в таблице
    print(len(presidents))

    # данные для конкретного президента, Трампа
    Trump_data = presidents['Trump']
    print(Trump_data)

    # есть ли президент с таким именем
    print('Trump' in presidents)

    # все президенты
    for president in presidents:
        print(president['name'])
