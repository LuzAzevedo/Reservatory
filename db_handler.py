import sqlite3
from threading import Lock
from datetime import datetime

class DBHandler():
    def __init__(self, db_path, tags, tablename="database") -> None:
        self._db_path = db_path
        self._tablename = tablename
        self._con = sqlite3.connect(self._db_path, check_same_thread=False)
        self._cursor = self._con.cursor()
        self._col_names = tags.keys()
        self._lock = Lock()
        self.create_table()
    
    def __del__(self):
        self._con.close()
    
    def create_table(self):
        self._lock.acquire()
        try:
            sql_str = f"""
            CREATE TABLE IF NOT EXISTS {self._tablename} (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                """
            for name in self._col_names:
                sql_str += f"{name} REAL,"
            sql_str = sql_str[:-1] + ");"
            
            
            self._cursor.execute(sql_str)
            self._con.commit()

        except Exception as e:
            print("Erro no create_table: ", e.args)
            
        self._lock.release()
    
    def insert_data(self, data):
        self._lock.acquire()
        try:
            timestamp = datetime.strftime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            str_cols = "timestamp, " + ", ".join( k for k in data["values"].keys())
            str_values = f"'{timestamp}', " + ", ".join([str(data["values"][k]) for k in data["values"].keys()])
            sql_str = f"INSERT INTO {self._tablename} ({str_cols}) VALUES ({str_values});"

            self._cursor.execute(sql_str)
            self._con.commit()
        except Exception as e:
            print("Erro no insert_data: ", e.args)
        
        self._lock.release()

    def select_data(self, cols, init_t, final_t):
        self._lock.acquire()
        
        try:
            sql_str = f"SELECT {', '.join(cols)} FROM {self._tablename} WHERE timestamp BETWEEN '{init_t}' AND '{final_t}';"

            self._cursor.execute(sql_str)
            dados = dict((sensor, []) for sensor in cols)
            for linha in self._cursor.fetchall():
                for d in range(0, len(linha)):
                    dados[cols[d]].append(linha[d])

            self._lock.release()
            return dados
        except Exception as e:
            print("Erro na selecao: ", e.args)

        self._lock.release()
