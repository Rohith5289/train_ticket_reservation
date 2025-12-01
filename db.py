import mysql.connector
from datetime import datetime

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "train_reservation"

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def init_db():
    conn = get_connection()
    conn.close()

def get_routes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT source, destination FROM trains")
    rows = cur.fetchall()
    conn.close()
    return rows

def search_schedules(source, destination, travel_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.schedule_id,
               t.train_number,
               t.train_name,
               s.travel_date,
               s.departure_time,
               s.arrival_time,
               s.fare,
               s.available_seats
        FROM schedules s
        JOIN trains t ON s.train_id = t.train_id
        WHERE t.source = %s
          AND t.destination = %s
          AND s.travel_date = %s
        """,
        (source, destination, travel_date)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def book_ticket(schedule_id, name, phone, email, seats):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT available_seats FROM schedules WHERE schedule_id = %s",
        (schedule_id,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("Schedule not found")

    available = row[0]
    if seats <= 0:
        conn.close()
        raise ValueError("Seats must be positive")
    if seats > available:
        conn.close()
        raise ValueError(f"Only {available} seats available")

    cur.execute(
        "INSERT INTO passengers (name, phone, email) VALUES (%s, %s, %s)",
        (name, phone, email if email else None)
    )
    passenger_id = cur.lastrowid

    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        """
        INSERT INTO bookings (schedule_id, passenger_id, seats_booked, booking_time, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (schedule_id, passenger_id, seats, booking_time, "CONFIRMED")
    )
    booking_id = cur.lastrowid

    cur.execute(
        "UPDATE schedules SET available_seats = available_seats - %s WHERE schedule_id = %s",
        (seats, schedule_id)
    )

    conn.commit()
    conn.close()
    return booking_id

def get_booking(booking_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT b.booking_id,
               b.status,
               b.seats_booked,
               b.booking_time,
               p.name,
               p.phone,
               p.email,
               s.travel_date,
               s.departure_time,
               s.arrival_time,
               s.fare,
               t.train_number,
               t.train_name,
               t.source,
               t.destination
        FROM bookings b
        JOIN passengers p ON b.passenger_id = p.passenger_id
        JOIN schedules s ON b.schedule_id = s.schedule_id
        JOIN trains t ON s.train_id = t.train_id
        WHERE b.booking_id = %s
        """,
        (booking_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row

def cancel_booking(booking_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT status, seats_booked, schedule_id FROM bookings WHERE booking_id = %s",
        (booking_id,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("Booking not found")

    status, seats, schedule_id = row
    if status == "CANCELLED":
        conn.close()
        raise ValueError("Booking already cancelled")

    cur.execute(
        "UPDATE bookings SET status = %s WHERE booking_id = %s",
        ("CANCELLED", booking_id)
    )
    cur.execute(
        "UPDATE schedules SET available_seats = available_seats + %s WHERE schedule_id = %s",
        (seats, schedule_id)
    )

    conn.commit()
    conn.close()
