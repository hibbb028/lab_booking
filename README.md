📖 About the Project: Lab Booking System
The Lab Booking System is a Flask-based web application backed by an SQLite database (lab_booking.db) designed for scheduling and reserving computer lab slots (such as CCF, AI Programming Labs, and System Labs).

Key Features:
Authentication: User login and session management via app.py.
Time & Day Selection: Allows users to choose days (Monday – Friday) and period hours (Hours 1 – 6).
Lab Slot Booking & Cancellation: Shows real-time availability of labs and enables users to book slots or cancel their own reservations.
Database Utilities:
setup_db.py
: Creates schema (users, labs) and seeds initial schedule data.
update_db.py
: Adds necessary columns (is_booked, booked_by).
cleanup_unknown_bookings.py
: Clears invalid or unassigned bookings.
