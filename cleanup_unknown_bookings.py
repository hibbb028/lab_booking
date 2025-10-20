import sqlite3

conn = sqlite3.connect("lab_booking.db")
cur = conn.cursor()

# Remove all bookings made by "Unknown" or without user
cur.execute("""
UPDATE labs
SET is_booked = 0,
    booked_by = NULL
WHERE booked_by IS NULL OR booked_by = '' OR booked_by = 'Unknown'
""")

conn.commit()
conn.close()

print("✅ All 'Unknown' bookings removed. Those labs are now available again.")
