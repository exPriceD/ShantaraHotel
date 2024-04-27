import sqlite3

from datetime import datetime


def booking_finish():
    database_path = '../instance/database.db'
    today_date = datetime.now().strftime('%d.%m.%Y')

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    new_status = "ended"

    update_query = "UPDATE bookings SET status = ? WHERE departure_date = ?"
    cursor.execute(update_query, (new_status, today_date))

    conn.commit()

    print(f"Updated {cursor.rowcount} bookings to status '{new_status}'.")

    cursor.close()
    conn.close()


booking_finish()

