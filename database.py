import sqlite3

class BotDB:
    
    def __init__(self, db_file): #соединение с БД
        self.con = sqlite3.connect(db_file)
        self.cursor = self.con.cursor()
    
    def user_exists(self, user_id): #проверка наличия юзера
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'user_id' = ?", (user_id, ))
        return bool(len(result.fetchall()))
    
    def get_user_id(self, user_id): #получение id юзера
        result = self.cursor.execute("SELECT 'id' FROM 'users' WHERE 'user_id' = ?", (user_id, ))
        return result.fetchone()[0]
    
    def add_user(self, user_id): #добавление юзера
        self.cursor.execute("INSERT or IGNORE into 'users' ('user_id') VALUES (?)", (user_id, ))
        return self.con.commit()
    
    def add_record(self, user_id, operation, value, category): #добавление записи о расходах и доходах
        self.cursor.execute("INSERT into 'records' ('user_id', 'operation', 'value', 'category') VALUES (?, ?, ?, ?)", (user_id, operation, value, category))
        return self.con.commit()
    
    def get_records(self, user_id): #получение истории операций
        result = self.cursor.execute("SELECT * FROM records WHERE user_id = ?", (user_id, ))
        return result.fetchall()

    def delete_record(self, user_id, record_date): #получение истории операций
        self.cursor.execute("DELETE FROM records WHERE user_id = ? AND date = ?", (user_id, record_date, ))
        self.con.commit()
        return '✅ Запись успешно удалена'
    
    def delete_all(self, user_id): #получение истории операций
        self.cursor.execute("DELETE FROM records WHERE user_id = ?", (user_id, ))
        self.con.commit()
        return '✅ Записи успешно удалены'

    def close(self): #закрытие
        self.con.close()