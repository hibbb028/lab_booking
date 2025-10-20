import sqlite3

conn = sqlite3.connect('lab_booking.db')
c = conn.cursor()

# --- Add 'is_booked' column if missing ---
try:
    c.execute("ALTER TABLE labs ADD COLUMN is_booked INTEGER DEFAULT 0;")
    print("✅ 'is_booked' column added successfully.")
except Exception as e:
    print("ℹ️ 'is_booked' column may already exist — skipping.", e)

# --- Add 'booked_by' column if missing ---
try:
    c.execute("ALTER TABLE labs ADD COLUMN booked_by TEXT DEFAULT NULL;")
    print("✅ 'booked_by' column added successfully.")
except Exception as e:
    print("ℹ️ 'booked_by' column may already exist — skipping.", e)

conn.commit()
conn.close()
print("✅ Database update completed successfully.")



