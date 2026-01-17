import sqlite3
from pathlib import Path

class Database:
    def __init__(self,path=None):
        self.path = path
        if path is None:
            self.path = Path.home() / ".config" / "Fileflow" / "logsDatabase.db"
        else:
            self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def getConnection(self):
        connection = sqlite3.connect(self.path)
        return connection

    def connect(self):
            self.connection = sqlite3.connect(self.path)
            cursor = self.connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS logs")
            cursor.execute("DROP TABLE IF EXISTS hashes")
            self.connection.commit()

    def tableCreation(self):
        cursor = self.connection.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                timestamp TEXT,
                status TEXT,
                fileName TEXT,
                fromPath TEXT,
                toPath TEXT,
                fileHash VARCHAR(64)
                );
            """
        )
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS hashes (
                fileHash VARCHAR(64) PRIMARY KEY
                );
            """
        )
        self.connection.commit()

    def inputLogs(self,timestamp,status,fileName,fromPath,toPath,fileHash):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)",(timestamp,status,fileName,fromPath,toPath,fileHash))
        self.connection.commit()
    
    def hashExists(self, fileHash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM hashes WHERE fileHash = ?", (fileHash,))
        count = cursor.fetchone()[0]
        return count > 0
    
    def getLogs(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        data = cursor.fetchall()
        return data

    def connectTerminate(self):
        self.connection.close()