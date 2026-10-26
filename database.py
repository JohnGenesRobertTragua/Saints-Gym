import os
import sqlite3

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Local development keeps using gym.db beside the application.
# Cloud deployments can point this to a persistent disk location
# through SAINTS_DATABASE_PATH.
DATABASE = os.environ.get(
    "SAINTS_DATABASE_PATH",
    os.path.join(BASE_DIR, "gym.db")
)

DATABASE_DIRECTORY = os.path.dirname(os.path.abspath(DATABASE))
if DATABASE_DIRECTORY:
    os.makedirs(DATABASE_DIRECTORY, exist_ok=True)



# ==========================================

# DATABASE CONNECTION

# ==========================================

def get_connection():







    connection = sqlite3.connect(



        DATABASE,



        timeout=10



    )



    connection.row_factory = sqlite3.Row

    connection.execute(



        "PRAGMA busy_timeout = 10000"



    )



    connection.execute(



        "PRAGMA foreign_keys = ON"



    )



    return connection



# ==========================================

# CREATE TABLES

# ==========================================

def create_tables():







    connection = get_connection()



    try:



        # ==================================

        # MEMBERS

        # ==================================



        connection.execute("""



            CREATE TABLE IF NOT EXISTS members (



                id INTEGER PRIMARY KEY AUTOINCREMENT,

                surname TEXT NOT NULL,

                first_name TEXT NOT NULL,

                phone TEXT NOT NULL,

                registered_at TIMESTAMP

                    DEFAULT CURRENT_TIMESTAMP,

                active INTEGER NOT NULL DEFAULT 1



            )



        """)



        # ==================================

        # ADD ACTIVE COLUMN TO EXISTING DATABASES

        # ==================================



        member_columns = connection.execute(

            "PRAGMA table_info(members)"

        ).fetchall()



        member_column_names = {

            column["name"]

            for column in member_columns

        }



        if "active" not in member_column_names:

            connection.execute("""

                ALTER TABLE members

                ADD COLUMN active INTEGER NOT NULL DEFAULT 1

            """)



        if "registration_status" not in member_column_names:

            connection.execute("""

                ALTER TABLE members

                ADD COLUMN registration_status TEXT NOT NULL DEFAULT 'approved'

            """)



        connection.execute("""
            CREATE TABLE IF NOT EXISTS released_member_ids (
                id INTEGER PRIMARY KEY,
                released_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)



        # ==================================

        # MEMBER CHECK-INS

        # ==================================



        connection.execute("""



            CREATE TABLE IF NOT EXISTS check_ins (



                id INTEGER PRIMARY KEY AUTOINCREMENT,

                member_id INTEGER NOT NULL,

                check_in_time TIMESTAMP NOT NULL,

                check_out_time TIMESTAMP,

                FOREIGN KEY (member_id)



                    REFERENCES members(id)



            )



        """)



        # ==================================

        # GUEST CHECK-INS

        # ==================================



        connection.execute("""



            CREATE TABLE IF NOT EXISTS guest_check_ins (



                id INTEGER PRIMARY KEY AUTOINCREMENT,

                surname TEXT NOT NULL,

                first_name TEXT NOT NULL,

                phone TEXT NOT NULL,

                check_in_time TIMESTAMP NOT NULL,

                check_out_time TIMESTAMP



            )



        """)



                # ==================================
        # PENDING MEMBER REGISTRATIONS
        # ==================================

        connection.execute("""
            CREATE TABLE IF NOT EXISTS pending_registrations (
                id INTEGER PRIMARY KEY,
                surname TEXT NOT NULL,
                first_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


        pending_rows = connection.execute("""
            SELECT id, surname, first_name, phone
            FROM pending_registrations
        """).fetchall()

        for pending_row in pending_rows:
            existing_pending_member = connection.execute("""
                SELECT id FROM members WHERE id = ?
            """, (pending_row["id"],)).fetchone()

            if existing_pending_member is None:
                connection.execute("""
                    INSERT INTO members
                    (id, surname, first_name, phone, active, registration_status)
                    VALUES (?, ?, ?, ?, 1, 'pending')
                """, (pending_row["id"], pending_row["surname"], pending_row["first_name"], pending_row["phone"]))
            else:
                connection.execute("""
                    UPDATE members
                    SET registration_status = 'pending'
                    WHERE id = ? AND active = 1
                """, (pending_row["id"],))


# ==================================

        # STAFF / ADMIN USERS

        # ==================================



        connection.execute("""



            CREATE TABLE IF NOT EXISTS staff_users (



                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                password TEXT NOT NULL,

                created_at TIMESTAMP



                    DEFAULT CURRENT_TIMESTAMP



            )



        """)

        # ==================================
        # STAFF ACCOUNT CLEANUP
        # ==================================
        # Saints Gym has ONE normal staff account. The owner/master
        # credentials are handled separately in app.py.
        # Older versions created an "admin / admin123" staff account.
        # Remove that legacy account so it cannot be used as a second
        # staff key.

        connection.execute("""
            DELETE FROM staff_users
            WHERE username = 'admin'
        """)

        connection.commit()



        # ==================================
        # STAFF PASSWORD SECURITY MIGRATION
        # ==================================
        staff_rows = connection.execute("""
            SELECT id, password
            FROM staff_users
        """).fetchall()

        for staff_row in staff_rows:
            stored_password = staff_row["password"] or ""

            # Werkzeug hashes used by this application start with scrypt:
            if stored_password and not stored_password.startswith("scrypt:"):
                connection.execute("""
                    UPDATE staff_users
                    SET password = ?
                    WHERE id = ?
                """, (
                    generate_password_hash(stored_password),
                    staff_row["id"]
                ))

        connection.commit()

    finally:

        connection.close()



# ==========================================

# GET NEXT CUSTOMER ID
# ==========================================


def _allocate_member_id(connection):
    # Reuse the oldest released ID only when it is genuinely unused.
    # This also cleans up stale release entries left by older database states.
    while True:
        released = connection.execute("""
            SELECT id
            FROM released_member_ids
            ORDER BY released_at ASC, id ASC
            LIMIT 1
        """).fetchone()

        if released is None:
            break

        released_id = int(released["id"])
        occupied = connection.execute("""
            SELECT 1
            FROM members
            WHERE id = ?
            UNION ALL
            SELECT 1
            FROM pending_registrations
            WHERE id = ?
            LIMIT 1
        """, (released_id, released_id)).fetchone()

        if occupied is not None:
            connection.execute(
                "DELETE FROM released_member_ids WHERE id = ?",
                (released_id,)
            )
            continue

        connection.execute(
            "DELETE FROM released_member_ids WHERE id = ?",
            (released_id,)
        )
        return released_id

    row = connection.execute("""
        SELECT MAX(id) AS max_id
        FROM (
            SELECT id FROM members
            UNION ALL
            SELECT id FROM pending_registrations
        )
    """).fetchone()
    return int(row["max_id"] or 0) + 1


def get_next_member_id():
    connection = get_connection()
    try:
        released_rows = connection.execute("""
            SELECT id
            FROM released_member_ids
            ORDER BY released_at ASC, id ASC
        """).fetchall()

        for released in released_rows:
            released_id = int(released["id"])
            occupied = connection.execute("""
                SELECT 1
                FROM members
                WHERE id = ?
                UNION ALL
                SELECT 1
                FROM pending_registrations
                WHERE id = ?
                LIMIT 1
            """, (released_id, released_id)).fetchone()

            if occupied is None:
                return f"{released_id:04d}"

        row = connection.execute("""
            SELECT MAX(id) AS max_id
            FROM (
                SELECT id FROM members
                UNION ALL
                SELECT id FROM pending_registrations
            )
        """).fetchone()
        return f"{int(row['max_id'] or 0) + 1:04d}"
    finally:
        connection.close()


# PENDING MEMBER REGISTRATIONS
# ==========================================

def add_pending_registration(surname, first_name, phone):
    connection = get_connection()
    try:
        next_id = _allocate_member_id(connection)

        connection.execute("""
            INSERT INTO members
            (id, surname, first_name, phone, active, registration_status)
            VALUES (?, ?, ?, ?, 1, 'pending')
        """, (next_id, surname.strip(), first_name.strip(), phone.strip()))

        connection.execute("""
            INSERT INTO pending_registrations
            (id, surname, first_name, phone)
            VALUES (?, ?, ?, ?)
        """, (next_id, surname.strip(), first_name.strip(), phone.strip()))

        connection.commit()
        return f"{next_id:04d}"
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_pending_registrations():


    connection = get_connection()


    try:


        return connection.execute("""

            SELECT

                id,

                surname,

                first_name,

                phone,

                submitted_at

            FROM pending_registrations

            ORDER BY submitted_at DESC, id DESC

        """).fetchall()


    finally:


        connection.close()





def get_pending_registration_count():


    connection = get_connection()


    try:


        row = connection.execute("""

            SELECT COUNT(*) AS total

            FROM pending_registrations

        """).fetchone()


        return int(row["total"])


    finally:


        connection.close()





def accept_pending_registration(registration_id):
    try:
        database_id = int(registration_id)
    except (ValueError, TypeError):
        return False, "Invalid registration ID."

    connection = get_connection()
    try:
        pending = connection.execute("""
            SELECT id, surname, first_name, phone
            FROM pending_registrations
            WHERE id = ?
        """, (database_id,)).fetchone()

        if pending is None:
            return False, "Pending registration not found."

        member = connection.execute("""
            SELECT id FROM members WHERE id = ? AND active = 1
        """, (database_id,)).fetchone()

        if member is None:
            connection.execute("""
                INSERT INTO members
                (id, surname, first_name, phone, active, registration_status)
                VALUES (?, ?, ?, ?, 1, 'approved')
            """, (pending["id"], pending["surname"], pending["first_name"], pending["phone"]))
        else:
            connection.execute("""
                UPDATE members SET registration_status = 'approved'
                WHERE id = ?
            """, (database_id,))

        connection.execute("DELETE FROM pending_registrations WHERE id = ?", (database_id,))
        connection.commit()
        return True, "Member registration accepted successfully."
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def reject_pending_registration(registration_id):
    try:
        database_id = int(registration_id)
    except (ValueError, TypeError):
        return False, "Invalid registration ID."

    connection = get_connection()
    try:
        pending = connection.execute("""
            SELECT id, surname, first_name, phone
            FROM pending_registrations
            WHERE id = ?
        """, (database_id,)).fetchone()

        if pending is None:
            return False, "Pending registration not found."

        visits = connection.execute("""
            SELECT check_in_time, check_out_time
            FROM check_ins
            WHERE member_id = ?
            ORDER BY id ASC
        """, (database_id,)).fetchall()

        for visit in visits:
            connection.execute("""
                INSERT INTO guest_check_ins
                (surname, first_name, phone, check_in_time, check_out_time)
                VALUES (?, ?, ?, ?, ?)
            """, (pending["surname"], pending["first_name"], pending["phone"], visit["check_in_time"], visit["check_out_time"]))

        connection.execute("DELETE FROM check_ins WHERE member_id = ?", (database_id,))

        # A pending_registrations row is the source of truth here. Remove its
        # temporary members row by ID even if an older migration left its
        # registration_status inconsistent; otherwise the released ID could
        # collide with the still-existing members row on the next registration.
        connection.execute("DELETE FROM members WHERE id = ?", (database_id,))
        connection.execute("DELETE FROM pending_registrations WHERE id = ?", (database_id,))
        connection.execute("""
            INSERT OR REPLACE INTO released_member_ids (id, released_at)
            VALUES (?, CURRENT_TIMESTAMP)
        """, (database_id,))

        connection.commit()
        if visits:
            return True, "Registration rejected. Temporary member attendance was converted to guest attendance, and the Customer ID was released."
        return True, "Registration rejected. The Customer ID was released for future use."
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


# ADD MEMBER

# ==========================================





def add_member(

    surname,

    first_name,

    phone

):



    connection = get_connection()



    try:

        next_id = _allocate_member_id(connection)



        connection.execute("""

            INSERT INTO members

            (

                id,

                surname,

                first_name,

                phone,

                active,

                registration_status

            )

            VALUES (?, ?, ?, ?, 1, 'approved')

        """, (

            next_id,

            surname,

            first_name,

            phone

        ))



        connection.commit()



        return f"{next_id:04d}"



    except Exception:

        connection.rollback()

        raise



    finally:

        connection.close()







# ==========================================

# MEMBER MANAGEMENT

# ==========================================





def get_all_members(search="", search_field="all"):



    connection = get_connection()



    try:

        query = """

            SELECT

                id,

                surname,

                first_name,

                phone,

                registered_at AS created_at

            FROM members

            WHERE active = 1
              AND registration_status = 'approved'

        """



        params = []

        search = (search or "").strip()



        if search:

            if search_field == "id":

                query += " AND printf('%04d', id) LIKE ?"

                params.append(f"%{search}%")



            elif search_field == "name":

                query += " AND LOWER(surname || ' ' || first_name) LIKE ?"

                params.append(f"%{search.lower()}%")



            elif search_field == "phone":

                query += " AND phone LIKE ?"

                params.append(f"%{search}%")



            else:

                query += (

                    " AND (printf('%04d', id) LIKE ?"

                    " OR LOWER(surname || ' ' || first_name) LIKE ?"

                    " OR phone LIKE ?)"

                )

                params.extend([

                    f"%{search}%",

                    f"%{search.lower()}%",

                    f"%{search}%"

                ])



        query += " ORDER BY registered_at DESC, id DESC"



        return connection.execute(

            query,

            params

        ).fetchall()



    finally:

        connection.close()





def update_member(

    member_id,

    surname,

    first_name,

    phone

):



    try:

        database_id = int(member_id)

    except (ValueError, TypeError):

        return False, "Invalid customer ID."



    connection = get_connection()



    try:

        member = connection.execute("""

            SELECT id

            FROM members

            WHERE id = ?

              AND active = 1

        """, (database_id,)).fetchone()



        if member is None:

            return False, "Member not found."



        connection.execute("""

            UPDATE members

            SET surname = ?,

                first_name = ?,

                phone = ?

            WHERE id = ?

        """, (

            surname.strip(),

            first_name.strip(),

            phone.strip(),

            database_id

        ))



        connection.commit()



        return True, "Member updated successfully."



    except Exception:

        connection.rollback()

        raise



    finally:

        connection.close()





def delete_member(member_id):



    try:

        database_id = int(member_id)

    except (ValueError, TypeError):

        return False, "Invalid customer ID."



    connection = get_connection()



    try:

        member = connection.execute("""

            SELECT id

            FROM members

            WHERE id = ?

              AND active = 1

        """, (database_id,)).fetchone()



        if member is None:

            return False, "Member not found."



        connection.execute("""

            UPDATE members

            SET active = 0

            WHERE id = ?

        """, (database_id,))



        connection.commit()



        return True, (

            "Member removed successfully. "

            "Attendance history has been preserved."

        )



    except Exception:

        connection.rollback()

        raise



    finally:

        connection.close()







# GET MEMBER



# ==========================================

def get_member(member_id):



    try:



        database_id = int(member_id)



    except (ValueError, TypeError):

        return None



    connection = get_connection()



    try:



        return connection.execute("""



            SELECT



                id,

                surname,

                first_name,

                phone,

                registered_at



            FROM members



            WHERE id = ?

              AND active = 1



        """, (



            database_id,



        )).fetchone()



    finally:



        connection.close()



# ==========================================

# MEMBER CHECK-IN

# ==========================================

def add_check_in(member_id):



    connection = get_connection()



    try:



        now = datetime.now()



        check_in_time = now.strftime(



            "%I:%M %p"



        )



        check_in_date = now.strftime(



            "%B %d, %Y"



        )



        full_check_in_time = (



            f"{check_in_date} | "



            f"{check_in_time}"



        )



        # Every check-in is recorded.

        # Previous check-ins do not matter.



        connection.execute("""



            INSERT INTO check_ins



            (



                member_id,

                check_in_time,

                check_out_time



            )



            VALUES (?, ?, NULL)



        """, (



            member_id,

            full_check_in_time



        ))



        connection.commit()



        return {



            "success": True,

            "check_in_time": check_in_time,

            "check_in_date": check_in_date



        }







    except Exception:



        connection.rollback()



        raise



    finally:



        connection.close()





# ==========================================

# MEMBER CHECK-OUT

# ==========================================

def check_out_member(member_id):



    connection = get_connection()



    try:



        now = datetime.now()

        check_out_time = now.strftime(



            "%I:%M %p"



        )



        check_out_date = now.strftime(



            "%B %d, %Y"



        )



        full_check_out_time = (



            f"{check_out_date} | "



            f"{check_out_time}"



        )



        visit = connection.execute("""



            SELECT



                id,

                check_in_time



            FROM check_ins

            WHERE member_id = ?



              AND check_out_time IS NULL



            ORDER BY id DESC



            LIMIT 1



        """, (



            member_id,



        )).fetchone()



        if visit is None:



            return {



                "success": False,

                "message": (



                    "No open check-in was found "

                    "for this member."



                )



            }



        connection.execute("""



            UPDATE check_ins

            SET check_out_time = ?

            WHERE id = ?



        """, (



            full_check_out_time,



            visit["id"]



        ))



        connection.commit()



        return {



            "success": True,

            "check_out_time": check_out_time,

            "check_out_date": check_out_date,

            "check_in_time": visit["check_in_time"]



        }



    except Exception:



        connection.rollback()

        raise



    finally:



        connection.close()



# ==========================================

# ADD GUEST CHECK-IN

# ==========================================

def add_guest_check_in(



    surname,



    first_name,



    phone



):



    connection = get_connection()



    try:



        now = datetime.now()

        check_in_time = now.strftime(



            "%I:%M %p"



        )



        check_in_date = now.strftime(



            "%B %d, %Y"



        )



        full_check_in_time = (



            f"{check_in_date} | "



            f"{check_in_time}"



        )



        cursor = connection.execute("""



            INSERT INTO guest_check_ins



            (



                surname,

                first_name,

                phone,

                check_in_time,

                check_out_time



            )



            VALUES (?, ?, ?, ?, NULL)



        """, (



            surname,

            first_name,

            phone,

            full_check_in_time



        ))



        guest_visit_id = cursor.lastrowid

        connection.commit()



        return {



            "success": True,

            "guest_visit_id": guest_visit_id,

            "check_in_time": check_in_time,

            "check_in_date": check_in_date



        }



    except Exception:



        connection.rollback()

        raise



    finally:



        connection.close()



# ==========================================

# GET OPEN GUEST VISIT BY PHONE
# ==========================================
def get_guest_open_visit(phone):

    connection = get_connection()

    try:
        legacy_phone = None
        if isinstance(phone, str) and phone.startswith("+63") and len(phone) == 13:
            legacy_phone = "0" + phone[3:]

        if legacy_phone:
            return connection.execute("""
                SELECT id, surname, first_name, phone, check_in_time
                FROM guest_check_ins
                WHERE phone IN (?, ?)
                  AND check_out_time IS NULL
                ORDER BY id DESC
                LIMIT 1
            """, (phone, legacy_phone)).fetchone()

        return connection.execute("""
            SELECT id, surname, first_name, phone, check_in_time
            FROM guest_check_ins
            WHERE phone = ?
              AND check_out_time IS NULL
            ORDER BY id DESC
            LIMIT 1
        """, (phone,)).fetchone()
    finally:
        connection.close()


# GUEST CHECK-OUT

# ==========================================

def check_out_guest(phone):



    connection = get_connection()



    try:



        now = datetime.now()

        check_out_time = now.strftime(



            "%I:%M %p"



        )



        check_out_date = now.strftime(



            "%B %d, %Y"



        )



        full_check_out_time = (



            f"{check_out_date} | "

            f"{check_out_time}"



        )



        # Accept both the new E.164 format and legacy Philippine
        # 11-digit guest records saved before international phone support.
        legacy_phone = None
        if isinstance(phone, str) and phone.startswith("+63") and len(phone) == 13:
            legacy_phone = "0" + phone[3:]

        if legacy_phone:
            visit = connection.execute("""
                SELECT
                    id,
                    surname,
                    first_name,
                    phone,
                    check_in_time
                FROM guest_check_ins
                WHERE phone IN (?, ?)
                  AND check_out_time IS NULL
                ORDER BY id DESC
                LIMIT 1
            """, (phone, legacy_phone)).fetchone()
        else:
            visit = connection.execute("""
                SELECT
                    id,
                    surname,
                    first_name,
                    phone,
                    check_in_time
                FROM guest_check_ins
                WHERE phone = ?
                  AND check_out_time IS NULL
                ORDER BY id DESC
                LIMIT 1
            """, (phone,)).fetchone()

        if visit is None:



            return {



                "success": False,

                "message": (



                    "No open guest check-in "

                    "was found for this "

                    "phone number."



                )



            }



        connection.execute("""



            UPDATE guest_check_ins

            SET check_out_time = ?

            WHERE id = ?



        """, (



            full_check_out_time,



            visit["id"]



        ))



        connection.commit()



        return {



            "success": True,

            "full_name": (



                f"{visit['surname']}, "



                f"{visit['first_name']}"



            ),



            "phone": visit["phone"],

            "check_in_time": (



                visit["check_in_time"]



            ),



            "check_out_time": check_out_time,

            "check_out_date": check_out_date



        }



    except Exception:



        connection.rollback()

        raise



    finally:



        connection.close()



def update_staff_credentials(



    new_username,

    new_password



):



    new_username = (new_username or "").strip()

    new_password = new_password or ""



    if not new_username:

        return False, "Username is required."



    if not new_password:

        return False, "Password is required."



    connection = get_connection()



    try:



        current = connection.execute("""



            SELECT id

            FROM staff_users

            ORDER BY id ASC

            LIMIT 1



        """).fetchone()



        existing = connection.execute("""



            SELECT id

            FROM staff_users

            WHERE username = ?



        """, (new_username,)).fetchone()



        if (

            existing is not None

            and (current is None or existing["id"] != current["id"])

        ):

            return False, "That username is already in use."



        if current is None:

            connection.execute("""



                INSERT INTO staff_users

                (username, password)

                VALUES (?, ?)



            """, (new_username, generate_password_hash(new_password)))



        else:

            connection.execute("""



                UPDATE staff_users

                SET username = ?,

                    password = ?

                WHERE id = ?



            """, (

                new_username,

                generate_password_hash(new_password),

                current["id"]

            ))



        connection.commit()



        return True, "Staff credentials updated successfully."



    except Exception:

        connection.rollback()

        raise



    finally:

        connection.close()





# ==========================================

# STAFF ACCOUNT SETTINGS

# ==========================================

def update_staff_username(



    current_username,

    new_username



):



    current_username = (current_username or "").strip()

    new_username = (new_username or "").strip()



    if not current_username:

        return False, "Current staff account was not found."



    if not new_username:

        return False, "Username is required."



    connection = get_connection()



    try:



        current = connection.execute("""

            SELECT id

            FROM staff_users

            WHERE username = ?

        """, (current_username,)).fetchone()



        if current is None:

            return False, "Current staff account was not found."



        existing = connection.execute("""

            SELECT id

            FROM staff_users

            WHERE username = ?

        """, (new_username,)).fetchone()



        if existing is not None and existing["id"] != current["id"]:

            return False, "That username is already in use."



        connection.execute("""

            UPDATE staff_users

            SET username = ?

            WHERE id = ?

        """, (new_username, current["id"]))



        connection.commit()



        return True, "Username changed successfully."



    except Exception:

        connection.rollback()

        raise



    finally:

        connection.close()





def update_staff_password(



    current_username,

    new_password



):



    current_username = (current_username or "").strip()

    new_password = new_password or ""



    if not current_username:

        return False, "Current staff account was not found."



    if not new_password:

        return False, "Password is required."



    connection = get_connection()



    try:



        current = connection.execute("""

            SELECT id

            FROM staff_users

            WHERE username = ?

        """, (current_username,)).fetchone()



        if current is None:

            return False, "Current staff account was not found."



        connection.execute("""

            UPDATE staff_users

            SET password = ?

            WHERE id = ?

        """, (generate_password_hash(new_password), current["id"]))



        connection.commit()



        return True, "Password changed successfully."



    except Exception:

        connection.rollback()

        raise



    finally:

        connection.close()





# ==========================================

# STAFF LOGIN

# ==========================================

def verify_staff_login(

    username,

    password

):

    connection = get_connection()

    try:

        staff = connection.execute("""

            SELECT

                id,

                username,

                password

            FROM staff_users

            WHERE username = ?

        """, (

            username,

        )).fetchone()

        if staff is None:

            return None

        stored_password = staff["password"] or ""

        # Existing installations may still contain a plaintext password.
        # Only call check_password_hash when the stored value is actually
        # a Werkzeug hash.
        if stored_password.startswith("scrypt:"):
            password_matches = check_password_hash(
                stored_password,
                password
            )
        else:
            password_matches = stored_password == password

            if password_matches:
                connection.execute("""
                    UPDATE staff_users
                    SET password = ?
                    WHERE id = ?
                """, (
                    generate_password_hash(password),
                    staff["id"]
                ))
                connection.commit()

        if not password_matches:
            return None

        return staff

    finally:

        connection.close()



def get_dashboard_statistics():



    connection = get_connection()



    try:



        today = datetime.now().strftime(



            "%B %d, %Y"



        )



        # Today's member check-ins



        member_checkins = connection.execute("""



            SELECT COUNT(*) AS total

            FROM check_ins

            WHERE check_in_time LIKE ?



        """, (



            f"{today} |%",



        )).fetchone()["total"]



        # Today's guest check-ins



        guest_checkins = connection.execute("""



            SELECT COUNT(*) AS total

            FROM guest_check_ins

            WHERE check_in_time LIKE ?



        """, (



            f"{today} |%",



        )).fetchone()["total"]



        # Total members



        total_members = connection.execute("""



            SELECT COUNT(*) AS total

            FROM members

            WHERE active = 1
              AND registration_status = 'approved'



        """).fetchone()["total"]





        # Currently inside:

        # distinct members with an open visit



        current_members = connection.execute("""



            SELECT COUNT(DISTINCT member_id) AS total

            FROM check_ins

            WHERE check_in_time LIKE ?
              AND check_out_time IS NULL



        """, (

            f"{today} |%",

        )).fetchone()["total"]





        # Currently inside:

        # distinct guests with an open visit



        current_guests = connection.execute("""



            SELECT COUNT(DISTINCT phone) AS total

            FROM guest_check_ins

            WHERE check_in_time LIKE ?
              AND check_out_time IS NULL



        """, (

            f"{today} |%",

        )).fetchone()["total"]



        return {



            "member_checkins": member_checkins,

            "guest_checkins": guest_checkins,

            "total_checkins": (



                member_checkins +

                guest_checkins



            ),







            "total_members": total_members,

            "currently_inside": (



                current_members +



                current_guests



            )



        }



    finally:



        connection.close()



# ==========================================

# TODAY'S ATTENDANCE

# ==========================================

def _sort_attendance_records(records, sort_by="date"):

    if sort_by == "name":

        records.sort(
            key=lambda row: str(row["full_name"] or "").casefold()
        )

        return records


    def check_in_sort_key(row):

        value = (row["check_in_time"] or "").strip()

        formats = (
            "%B %d, %Y | %I:%M %p",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        )

        for date_format in formats:
            try:
                return datetime.strptime(
                    value,
                    date_format
                )
            except ValueError:
                continue

        # Legacy records may contain only a time. Use today's date
        # so those records still participate in chronological sorting.
        for time_format in ("%I:%M %p", "%H:%M"):
            try:
                parsed_time = datetime.strptime(
                    value,
                    time_format
                ).time()
                today = datetime.now().date()
                return datetime.combine(
                    today,
                    parsed_time
                )
            except ValueError:
                continue

        return datetime.min


    records.sort(
        key=check_in_sort_key,
        reverse=True
    )

    return records


def get_today_attendance(sort_by="date"):



    connection = get_connection()



    try:



        today = datetime.now().strftime(



            "%B %d, %Y"



        )



        members = connection.execute("""



            SELECT



                printf('%04d', m.id)



                    AS customer_id,



                m.surname || ', ' ||

                m.first_name



                    AS full_name,



                m.phone



                    AS phone,



                'Member'



                    AS visit_type,



                c.check_in_time,

                c.check_out_time



            FROM check_ins c



            INNER JOIN members m



                ON m.id = c.member_id



            WHERE c.check_in_time LIKE ?

            ORDER BY c.id DESC



        """, (



            f"{today} |%",



        )).fetchall()





        guests = connection.execute("""



            SELECT



                '-'



                    AS customer_id,





                surname || ', ' ||



                first_name



                    AS full_name,





                phone



                    AS phone,



                'Guest'



                    AS visit_type,



                check_in_time,

                check_out_time



            FROM guest_check_ins

            WHERE check_in_time LIKE ?

            ORDER BY id DESC



        """, (



            f"{today} |%",



        )).fetchall()



        records = list(members) + list(guests)

        return _sort_attendance_records(

            records,

            sort_by

        )



    finally:



        connection.close()



# ==========================================

# ATTENDANCE HISTORY

# ==========================================





def get_attendance_history(search="", selected_date="", sort_by="date"):



    connection = get_connection()



    try:



        search = (search or "").strip()

        selected_date = (selected_date or "").strip()



        date_pattern = ""



        if selected_date:

            try:

                date_object = datetime.strptime(

                    selected_date,

                    "%Y-%m-%d"

                )



                date_pattern = date_object.strftime(

                    "%B %d, %Y"

                )



            except ValueError:

                date_pattern = ""



        members = connection.execute("""

            SELECT

                printf('%04d', m.id)

                    AS customer_id,

                c.id

                    AS attendance_id,

                'member'

                    AS attendance_source,

                m.surname || ', ' ||

                m.first_name

                    AS full_name,

                m.phone

                    AS phone,

                'Member'

                    AS visit_type,

                c.check_in_time,

                c.check_out_time

            FROM check_ins c

            INNER JOIN members m

                ON m.id = c.member_id

            WHERE (

                ? = ''

                OR c.check_in_time LIKE ?

            )

            ORDER BY c.id DESC

        """, (

            date_pattern,

            f"{date_pattern} |%"

        )).fetchall()



        guests = connection.execute("""

            SELECT

                '-'

                    AS customer_id,

                id

                    AS attendance_id,

                'guest'

                    AS attendance_source,

                surname || ', ' ||

                first_name

                    AS full_name,

                phone

                    AS phone,

                'Guest'

                    AS visit_type,

                check_in_time,

                check_out_time

            FROM guest_check_ins

            WHERE (

                ? = ''

                OR check_in_time LIKE ?

            )

            ORDER BY id DESC

        """, (

            date_pattern,

            f"{date_pattern} |%"

        )).fetchall()



        records = list(members) + list(guests)



        if search:

            search_lower = search.lower()



            records = [

                row

                for row in records

                if search_lower in str(

                    row["customer_id"]

                ).lower()

                or search_lower in str(

                    row["full_name"]

                ).lower()

                or search_lower in str(

                    row["phone"]

                ).lower()

                or search_lower in str(

                    row["visit_type"]

                ).lower()

                or search_lower in str(

                    row["check_in_time"]

                ).lower()

                or search_lower in str(

                    row["check_out_time"] or ""

                ).lower()

            ]

        return _sort_attendance_records(

            records,

            sort_by

        )



    finally:

        connection.close()





# ==========================================
# DELETE ATTENDANCE RECORDS
# ==========================================

def delete_attendance_records(record_keys):
    """
    Permanently delete one or more attendance records.

    Each record key must be in the form:
        member:<check_ins.id>
        guest:<guest_check_ins.id>

    This function intentionally does not delete members themselves.
    It only removes the selected attendance visit records.
    """
    if not isinstance(record_keys, (list, tuple)):
        return False, "No attendance records were selected."

    normalized_keys = []

    for key in record_keys:
        if not isinstance(key, str):
            continue

        key = key.strip()

        if ":" not in key:
            continue

        source, raw_id = key.split(":", 1)
        source = source.strip().lower()
        raw_id = raw_id.strip()

        if source not in ("member", "guest"):
            continue

        try:
            record_id = int(raw_id)
        except (ValueError, TypeError):
            continue

        if record_id <= 0:
            continue

        normalized_keys.append((source, record_id))

    # Remove duplicates while preserving the submitted order.
    normalized_keys = list(dict.fromkeys(normalized_keys))

    if not normalized_keys:
        return False, "No valid attendance records were selected."

    connection = get_connection()

    try:
        deleted_count = 0

        for source, record_id in normalized_keys:

            if source == "member":
                cursor = connection.execute(
                    """
                    DELETE FROM check_ins
                    WHERE id = ?
                    """,
                    (record_id,)
                )

            else:
                cursor = connection.execute(
                    """
                    DELETE FROM guest_check_ins
                    WHERE id = ?
                    """,
                    (record_id,)
                )

            deleted_count += cursor.rowcount

        if deleted_count == 0:
            connection.rollback()
            return False, "The selected attendance records could not be found."

        connection.commit()

        return True, deleted_count

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()




# Backward-compatible name used by app.py

remove_member = delete_member
