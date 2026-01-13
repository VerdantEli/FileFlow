# FileFlow - Lightweight File Organizer

---

FileFlow is a lightweight file organizer written mainly in Python with MySQL. This application aims to fix that by automating file classification through a rule-based engine that organizes files into logical directory structures based on file type, age, and user-defined conditions.   

The primary goal of the file organizer is to eliminate digital clutter and improve file management efficiency by automating the organization of local directories.
Specific Objectives:
-	Automated Classification: To implement a rule-based engine that identifies files by their extensions and moves them to pre-defined, logical locations.
-	Storage Optimization: To reduce disk space wastage by identifying and removing duplicate files using cryptographic hashing (SHA-256).
-	Transactional Logging: To utilize an SQL database to record every file operation, providing the user with a searchable history and the ability to undo accidental moves.

## TO-DO LIST
- Organization Process (done)
- Duplicate Detector (done)
- Undo Button (done)
- Authorization
- Rules Making
- Settings/Configuration
- Background Process
- UI Enhancements
