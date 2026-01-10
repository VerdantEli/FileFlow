import sqlite3

class Database:
    def connect(self):
        self.connection = sqlite3.connect("organize.db")

    def tableCreation(self):
        cursor = self.connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                timestamp TEXT,
                status TEXT,
                fileName TEXT,
                fromPath TEXT,
                toPath TEXT
                );
            """
        )
        self.connection.commit()

    def inputLogs(self,timestamp,status,fileName,fromPath,toPath):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?)",(timestamp,status,fileName,fromPath,toPath))
        self.connection.commit()
    
    def getLogs(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        data = cursor.fetchmany(5)
        return data


    def connectTerminate(self):
        self.connection.close()