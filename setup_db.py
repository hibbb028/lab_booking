import sqlite3

# Connect to SQLite database (creates file if not exists)

conn = sqlite3.connect("lab_booking.db")
cursor = conn.cursor()

# Drop existing tables (for clean re-runs)

cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS labs")

# Create users table

cursor.execute("""
CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
password TEXT NOT NULL
)
""")

# Create labs table

cursor.execute("""
CREATE TABLE labs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
day TEXT NOT NULL,
hour INTEGER NOT NULL,
lab_name TEXT NOT NULL,
is_booked INTEGER DEFAULT 0
)
""")

# Insert sample users

users_data = [
("student1", "pass123"),
("student2", "pass456")
]
cursor.executemany("INSERT INTO users (username, password) VALUES (?, ?)", users_data)

# Insert labs data

labs_data = [
# Monday
("Monday", 3, "CCF"),
("Monday", 4, "CCF"),
("Monday", 5, "CCF"),
("Monday", 6, "CCF"),
("Monday", 1, "AI Programming Lab1"),
("Monday", 2, "AI Programming Lab1"),
("Monday", 1, "AI Programming Lab2"),
("Monday", 2, "AI Programming Lab2"),
("Monday", 3, "AI Programming Lab2"),
("Monday", 3, "System Lab1"),
("Monday", 4, "System Lab1"),
("Monday", 1, "System Lab2"),
("Monday", 2, "System Lab2"),


# Tuesday
("Tuesday", 3, "CCF"),

# Wednesday
("Wednesday", 1, "System Lab1"),
("Wednesday", 2, "System Lab1"),
("Wednesday", 3, "System Lab1"),
("Wednesday", 4, "System Lab1"),
("Wednesday", 1, "AI Programming Lab1"),
("Wednesday", 1, "AI Programming Lab2"),
("Wednesday", 5, "AI Programming Lab2"),
("Wednesday", 6, "AI Programming Lab2"),
("Wednesday", 1, "System Lab2"),
("Wednesday", 2, "System Lab2"),

# Thursday
("Thursday", 4, "AI Programming Lab1"),
("Thursday", 5, "AI Programming Lab1"),
("Thursday", 6, "AI Programming Lab1"),
("Thursday", 4, "AI Programming Lab2"),

# Friday
("Friday", 3, "CCF"),
("Friday", 4, "AI Programming Lab1"),
("Friday", 5, "AI Programming Lab1"),
("Friday", 6, "AI Programming Lab1"),
("Friday", 1, "System Lab1"),
("Friday", 5, "System Lab1"),
("Friday", 6, "System Lab1"),
("Friday", 1, "System Lab2")

]

cursor.executemany(
"INSERT INTO labs (day, hour, lab_name, is_booked) VALUES (?, ?, ?, 0)",
labs_data
)

conn.commit()
conn.close()

print("✅ Database setup complete! Tables 'users' and 'labs' created successfully.")
