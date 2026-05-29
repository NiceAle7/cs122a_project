import sys
import os
import csv
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host = 'localhost',
        user='test',
        password='password',
        database='cs122a'
    )

def print_bool(success: bool):
    print("Success" if success else "Fail")

def print_table(rows):
    for row in rows:
        print(','.join('' if v is None else str(v) for v in row))


def import_data(folder: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        for t in ["Approval", "Hosting", "Slot", "Event",
                  "OnCampus", "OffCampus", "Venue",
                  "Administrator", "Participant", "Organizer", "User"]:
            cursor.execute(f"DROP TABLE IF EXISTS {t};")

        ddl_statements = [
            """
            CREATE TABLE User (
                uid INT,
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                joined DATE NOT NULL,
                PRIMARY KEY (uid)
            )
            """,
            """
            CREATE TABLE Organizer (
                uid INT,
                department TEXT NOT NULL,
                experience INT NOT NULL,
                PRIMARY KEY (uid),
                FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE Participant (
                uid INT,
                type TEXT,
                PRIMARY KEY (uid),
                FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE Administrator (
                uid INT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                PRIMARY KEY (uid),
                FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE Event (
                eid INT,
                creator_uid INT NOT NULL,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                datetime DATETIME NOT NULL,
                PRIMARY KEY (eid),
                FOREIGN KEY (creator_uid) REFERENCES Organizer(uid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE Slot (
                eid INT,
                snum INT NOT NULL,
                is_reserved BOOLEAN NOT NULL,
                uid INT,
                PRIMARY KEY (eid, snum),
                FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
                FOREIGN KEY (uid) REFERENCES Participant(uid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE Venue (
                vid INT,
                street TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                zip TEXT NOT NULL,
                PRIMARY KEY (vid)
            )
            """,
            """
            CREATE TABLE OnCampus (
                vid INT,
                code TEXT NOT NULL,
                PRIMARY KEY (vid),
                FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE OffCampus (
                vid INT,
                distance INT NOT NULL,
                PRIMARY KEY (vid),
                FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE Hosting (
                eid INT NOT NULL,
                vid INT NOT NULL,
                is_primary BOOLEAN NOT NULL,
                PRIMARY KEY (eid, vid),
                FOREIGN KEY (eid) REFERENCES Event(eid) ON DELETE CASCADE,
                FOREIGN KEY (vid) REFERENCES Venue(vid) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE Approval (
                uid INT NOT NULL,
                vid INT NOT NULL,
                valid_from DATE NOT NULL,
                valid_until DATE NOT NULL,
                PRIMARY KEY (uid, vid),
                FOREIGN KEY (uid) REFERENCES Administrator(uid) ON DELETE CASCADE,
                FOREIGN KEY (vid) REFERENCES OffCampus(vid) ON DELETE CASCADE
            )
            """,
        ]

        for stmt in ddl_statements:
            cursor.execute(stmt)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        table_files = [
            ("User",          "User.csv"),
            ("Organizer",     "Organizer.csv"),
            ("Participant",   "Participant.csv"),
            ("Administrator", "Administrator.csv"),
            ("Event",         "Event.csv"),
            ("Slot",          "Slot.csv"),
            ("Venue",         "Venue.csv"),
            ("OnCampus",      "OnCampus.csv"),
            ("OffCampus",     "OffCampus.csv"),
            ("Hosting",       "Hosting.csv"),
            ("Approval",      "Approval.csv"),
        ]

        for table, filename in table_files:
            filepath = os.path.join(folder, filename)
            if not os.path.exists(filepath):
                continue
            with open(filepath, newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
            if not rows:
                continue
            placeholders = ','.join(['%s'] * len(rows[0]))
            sql = f"INSERT INTO {table} VALUES ({placeholders})"
            cleaned = [tuple(None if v in ('', 'NULL') else v for v in row) for row in rows]
            cursor.executemany(sql, cleaned)

        conn.commit()
        cursor.close()
        conn.close()
        print_bool(True)
    except Exception as e:
        print_bool(False)

def main():
    import_data('sample_data')

if __name__ == '__main__':
    main()