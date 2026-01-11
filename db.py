import sqlite3


class DatabaseManager:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self, table_name, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_or_create(self, table_name, data):
        try:
            query = f"SELECT * FROM {table_name} WHERE {' AND '.join(f'{key}=?' for key in data)}"
            row = self.cursor.execute(query, tuple(data.values())).fetchone()
            if row is None:
                values = tuple(data.values())
                # self.cursor.execute(
                # f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join('?' * len(data))})", values)
                self.insert_data(table_name, data)
                # self.conn.commit()
                # return self.get(table_name, **data)
            else:
                return row
        except Exception as e:
            print(f"Error: {e}")
            return None

    def select_data(self, table_name, columns, condition=None):
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_data(self, table_name, columns, condition):
        placeholders = ', '.join(['= ?'] * len(columns))
        query = f"UPDATE {table_name} SET {', '.join(columns)} WHERE {condition}"
        self.cursor.execute(query, columns)
        self.conn.commit()

    def delete_data(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query)
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

database = DatabaseManager("training.db")
    
def create_tables(db):
    # -- Таблица пользователей
    db.create_table("users", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "username TEXT NOT NULL",
        "email TEXT NOT NULL",
        "password TEXT NOT NULL"
    ])
    # -- Таблица упражнений (справочник)
    db.create_table("exercises", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "name TEXT NOT NULL UNIQUE",
        "description TEXT"
    ])
    # -- Таблица тренировок
    db.create_table("workouts", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id INTEGER NOT NULL",
        "start_time TIMESTAMP NOT NULL",
        "end_time TIMESTAMP",
        "duration INTEGER",
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
    ])
    # -- Таблица настроек тренировки
    db.create_table("workout_plans", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id INTEGER NOT NULL",
        "exercise_id INTEGER NOT NULL",        
        "sets_count INTEGER DEFAULT 3",
        "target_reps INTEGER",
        "rest_time_seconds INTEGER DEFAULT 30", # время отдыха после подхода в сек
        "notify_before INTEGER DEFAULT 10",
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
        "FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE",
        "UNIQUE(user_id, exercise_id)",
    ])
    # -- Таблица подходов (основная таблица с данными выполнения)
    db.create_table("sets", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "workout_id INTEGER NOT NULL",
        "exercise_id INTEGER NOT NULL",
        "set_number INTEGER NOT NULL",
        "reps INTEGER",    # -- количество повторений
        "duration INTEGER",    # -- время выполнения подхода в сек
        "rest_time INTEGER",    # -- время отдыха после подхода в сек
        "notes TEXT",
        "FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE",
        "FOREIGN KEY (exercise_id) REFERENCES exercises(id)",
        "UNIQUE(workout_id, exercise_id, set_number)",
    ])

    db.get_or_create("exercises", {
                     "name": "Отжимания", "description": "отжимания от пола"})
    db.get_or_create("exercises", {
                     "name": "Приседания", "description": "приседания без веса"})
    db.get_or_create("users", {'username': "Alex",
                     'email': "test@gmail.com", 'password': "123"})

create_tables(database)

if __name__ == "__main__":
    db = DatabaseManager("test.db")
    # -- Таблица пользователей
    db.create_table("users", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "username TEXT NOT NULL",
        "email TEXT NOT NULL",
        "password TEXT NOT NULL"
    ])
    # -- Таблица упражнений (справочник)
    db.create_table("exercises", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "name TEXT NOT NULL UNIQUE",
        "description TEXT"
    ])
    # -- Таблица тренировок
    db.create_table("workouts", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id INTEGER NOT NULL",
        "start_time TIMESTAMP NOT NULL",
        "end_time TIMESTAMP",
        "duration INTEGER",
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
    ])
    # -- Таблица настроек тренировки
    db.create_table("workout_plans", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id INTEGER NOT NULL",
        "exercise_id INTEGER NOT NULL",        
        "sets_count INTEGER DEFAULT 3",
        "target_reps INTEGER",
        "rest_time_seconds INTEGER DEFAULT 30", # время отдыха после подхода в сек
        "notify_before INTEGER DEFAULT 10",
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
        "FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE",
        "UNIQUE(user_id, exercise_id)",
    ])
    # -- Таблица подходов (основная таблица с данными выполнения)
    db.create_table("sets", [
        "id INTEGER PRIMARY KEY AUTOINCREMENT",
        "workout_id INTEGER NOT NULL",
        "exercise_id INTEGER NOT NULL",
        "set_number INTEGER NOT NULL",
        "reps INTEGER",    # -- количество повторений
        "duration INTEGER",    # -- время выполнения подхода в сек
        "rest_time INTEGER",    # -- время отдыха после подхода в сек
        "notes TEXT",
        "FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE",
        "FOREIGN KEY (exercise_id) REFERENCES exercises(id)",
        "UNIQUE(workout_id, exercise_id, set_number)",
    ])

    db.get_or_create("exercises", {
                     "name": "Отжимания", "description": "отжимания от пола"})
    db.get_or_create("exercises", {
                     "name": "Приседания", "description": "приседания без веса"})
    db.get_or_create("users", {'username': "Alex",
                     'email': "test@gmail.com", 'password': "123"})

    # -- Начало тренировки
    # INSERT INTO workouts (user_id, name, start_time)
    # VALUES (1, '2024-01-15 08:00:00');

    db.insert_data("workouts", {"user_id": 1, "start_time": '2024-01-15 08:00:00'})

    # -- Добавление подходов
    # INSERT INTO sets (workout_id, exercise_id, set_number, reps, weight, duration, rest_time) VALUES
    # (1, 1, 1, 15, NULL, 30, 60),  -- отжимания, 1 подход
    # (1, 1, 2, 12, NULL, 25, 60),  -- отжимания, 2 подход
    # (1, 2, 1, 20, NULL, 40, 45);  -- приседания, 1 подход

    db.insert_data("sets", {
        "workout_id": 1, "exercise_id": 1, "set_number": 2, "reps": 14, "duration": 30, "rest_time": 60
    })


