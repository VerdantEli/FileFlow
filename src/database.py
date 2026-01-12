import mysql.connector

class Database:
    def connect(self):
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password ="root"
            )
            cursor = self.connection.cursor()
            cursor.execute("drop database logsdatabase")
            cursor.execute("CREATE DATABASE IF NOT EXISTS logsDatabase")
            cursor.execute("USE logsDatabase")
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
        cursor.execute("INSERT INTO logs VALUES (%s,%s,%s,%s,%s,%s)",(timestamp,status,fileName,fromPath,toPath,fileHash))
        self.connection.commit()
    
    def hashExists(self, fileHash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM hashes WHERE fileHash = %s", (fileHash,))
        count = cursor.fetchone()[0]
        return count > 0
    
    def getLogs(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        data = cursor.fetchall()
        return data

    def insertHash(self, fileHash):
        cursor = self.connection.cursor()
        cursor.execute("INSERT IGNORE INTO hashes VALUES (%s)", (fileHash,))
        self.connection.commit()

    def deleteHash(self, fileHash):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM hashes WHERE fileHash = %s", (fileHash,))
        self.connection.commit()


    def connectTerminate(self):
        self.connection.close()