import sqlite3

class Sqlite:

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def add_music(self, file_id, group_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO 'audio' VALUES (?,?)",(file_id, group_id))
    
    def get_by_group_id(self, group_id):
        with self.connection:
            msg_dict = []
            msg_id = self.cursor.execute(f"SELECT msg_id FROM 'audio' WHERE group_id = {int(group_id)}").fetchall()
            for msg_ in msg_id:
                for msg_ids in msg_:
                    msg_dict.append(msg_ids)
            return msg_dict

    def get_group_id(self):
        with self.connection:
            group_dict = []
            group_id = self.cursor.execute(f"SELECT group_id FROM 'audio'").fetchall()
            for group in group_id:
                for group_ids in group:
                    group_dict.append(group_ids)
            return group_dict
