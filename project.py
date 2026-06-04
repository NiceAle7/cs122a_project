import sys
import os
import csv
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='test',
        password='password',
        database='cs122a'
    )


def print_bool(success: bool):
    print("Success" if success else "Fail")


def print_table(rows):
    for row in rows:
        print(','.join('NULL' if v is None else str(v) for v in row))


def parse_null(v):
    """Treat the literal NULL (and empty string) as Python None."""
    if v is None or v == 'NULL' or v == '':
        return None
    return v


def parse_bool(v):
    """Parse a command-line boolean ('true'/'false') into 1/0."""
    return 1 if str(v).strip().lower() == 'true' else 0


# 1. Import data
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
            cleaned = [tuple(parse_null(v) for v in row) for row in rows]
            cursor.executemany(sql, cleaned)

        conn.commit()
        cursor.close()
        conn.close()
        print_bool(True)
    except Exception:
        print_bool(False)


# 2. Insert administrator
def insert_admin(uid, email, username, joined, firstname, lastname):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO User (uid, email, username, joined) VALUES (%s, %s, %s, %s)",
            (uid, email, username, joined)
        )
        cursor.execute(
            "INSERT INTO Administrator (uid, firstname, lastname) VALUES (%s, %s, %s)",
            (uid, firstname, lastname)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print_bool(True)
    except Exception:
        print_bool(False)


# 3. Add venue to event
def add_venue(eid, vid, is_primary):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if is_primary:
            cursor.execute(
                "SELECT 1 FROM Hosting WHERE eid = %s AND is_primary = 1",
                (eid,)
            )
            if cursor.fetchone() is not None:
                cursor.close()
                conn.close()
                print_bool(False)
                return
        cursor.execute(
            "INSERT INTO Hosting (eid, vid, is_primary) VALUES (%s, %s, %s)",
            (eid, vid, is_primary)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print_bool(True)
    except Exception:
        print_bool(False)


# 4. Reserve slot
def reserve_slot(eid, snum, uid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Slot SET is_reserved = 1, uid = %s "
            "WHERE eid = %s AND snum = %s AND is_reserved = 0",
            (uid, eid, snum)
        )
        success = cursor.rowcount == 1
        conn.commit()
        cursor.close()
        conn.close()
        print_bool(success)
    except Exception:
        print_bool(False)


# 5. Cancel reservation
def cancel_reservation(eid, snum, uid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Slot SET is_reserved = 0, uid = NULL "
            "WHERE eid = %s AND snum = %s AND is_reserved = 1 AND uid = %s",
            (eid, snum, uid)
        )
        success = cursor.rowcount == 1
        conn.commit()
        cursor.close()
        conn.close()
        print_bool(success)
    except Exception:
        print_bool(False)


# 6. Update event
def update_event(eid, title, datetime_val):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Event WHERE eid = %s", (eid,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            print_bool(False)
            return
        cursor.execute(
            "UPDATE Event SET title = %s, datetime = %s WHERE eid = %s",
            (title, datetime_val, eid)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print_bool(True)
    except Exception:
        print_bool(False)


# 7. Delete organizer
def delete_organizer(uid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Organizer WHERE uid = %s", (uid,))
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        print_bool(success)
    except Exception:
        print_bool(False)


# 8. Upcoming events with available slots
def available_events(date):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.eid, e.title, e.type, e.datetime, COUNT(s.snum) AS availableSlots
            FROM Event e
            JOIN Slot s ON s.eid = e.eid AND s.is_reserved = 0
            WHERE e.datetime > %s
            GROUP BY e.eid, e.title, e.type, e.datetime
            ORDER BY e.datetime ASC, e.eid ASC
            """,
            (date,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        print_table(rows)
    except Exception:
        pass


# 9. Popular event types
def popular_event_types(n):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.type, COUNT(*) AS reservedCount
            FROM Event e
            JOIN Slot s ON s.eid = e.eid
            WHERE s.is_reserved = 1
            GROUP BY e.type
            HAVING COUNT(*) >= %s
            ORDER BY reservedCount DESC, e.type ASC
            """,
            (n,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        print_table(rows)
    except Exception:
        pass


# 10. Participant schedule
def participant_schedule(uid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.eid, e.title, e.type, e.datetime, s.snum,
                   v.vid, v.street, v.city, v.state, v.zip
            FROM Slot s
            JOIN Event e ON e.eid = s.eid
            LEFT JOIN Hosting h ON h.eid = e.eid AND h.is_primary = 1
            LEFT JOIN Venue v ON v.vid = h.vid
            WHERE s.uid = %s AND s.is_reserved = 1
            ORDER BY e.datetime ASC, e.eid ASC
            """,
            (uid,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        print_table(rows)
    except Exception:
        pass


# 11. Organizer event count
def organizer_stats(n):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.uid, u.username, o.department, COUNT(e.eid) AS eventCount
            FROM Organizer o
            JOIN User u ON u.uid = o.uid
            JOIN Event e ON e.creator_uid = o.uid
            GROUP BY o.uid, u.username, o.department
            HAVING COUNT(e.eid) >= %s
            ORDER BY eventCount DESC, o.uid ASC
            """,
            (n,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        print_table(rows)
    except Exception:
        pass


# 12. Venue event list
def venue_events(vid):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.eid, e.title, e.type, e.datetime, h.is_primary
            FROM Hosting h
            JOIN Event e ON e.eid = h.eid
            WHERE h.vid = %s
            ORDER BY e.datetime ASC, e.eid ASC
            """,
            (vid,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        print_table(rows)
    except Exception:
        pass


def main():
    args = sys.argv
    func = args[1]
    p = [parse_null(x) for x in args[2:]]

    if func == "import":
        import_data(p[0])
    elif func == "insertAdmin":
        insert_admin(int(p[0]), p[1], p[2], p[3], p[4], p[5])
    elif func == "addVenue":
        add_venue(int(p[0]), int(p[1]), parse_bool(p[2]))
    elif func == "reserveSlot":
        reserve_slot(int(p[0]), int(p[1]), int(p[2]))
    elif func == "cancelReservation":
        cancel_reservation(int(p[0]), int(p[1]), int(p[2]))
    elif func == "updateEvent":
        update_event(int(p[0]), p[1], p[2])
    elif func == "deleteOrganizer":
        delete_organizer(int(p[0]))
    elif func == "availableEvents":
        available_events(p[0])
    elif func == "popularEventTypes":
        popular_event_types(int(p[0]))
    elif func == "participantSchedule":
        participant_schedule(int(p[0]))
    elif func == "organizerStats":
        organizer_stats(int(p[0]))
    elif func == "venueEvents":
        venue_events(int(p[0]))


if __name__ == '__main__':
    main()
