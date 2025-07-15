import mysql.connector
import hashlib
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

# Database Setup
def create_connection():
    """Creates and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",          # or "127.0.0.1"
            user="root",      # replace with your MySQL username
            password="password",  # replace with your MySQL password
            database="cycle_tracker"   # replace with your database name
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_table():
    """Creates a users table if it does not exist."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def hash_password(password):
    """Returns a hashed version of the password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Registers a new user with hashed password."""
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        print("Registration successful!")
    except mysql.connector.IntegrityError:
        print("Username already exists. Please choose a different username.")
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    """Logs in a user by verifying username and hashed password."""
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        print("Login successful!")
        return True
    else:
        print("Invalid username or password.")
        return False

# Menstrual Cycle Tracker Functions (same as before, included here for completeness)
def hormone_levels(day, cycle_length=28):
    max_estrogen = 200
    min_estrogen = 50
    max_progesterone = 25
    min_progesterone = 1
    estrogen = min_estrogen + (max_estrogen - min_estrogen) * np.sin(np.pi * day / cycle_length)
    if day < cycle_length / 2:
        progesterone = min_progesterone
    else:
        progesterone = min_progesterone + (max_progesterone - min_progesterone) * np.sin(np.pi * (day - cycle_length / 2) / (cycle_length / 2))
    return estrogen, progesterone

def predict_ovulation_phase(cycle_length=28):
    ovulation_day = cycle_length // 2
    ovulation_window = (ovulation_day - 2, ovulation_day + 2)
    max_estrogen = 200
    min_estrogen = 50
    estrogen_levels = [min_estrogen + (max_estrogen - min_estrogen) * np.sin(np.pi * day / cycle_length) for day in range(1, cycle_length + 1)]
    return ovulation_day, ovulation_window, estrogen_levels

def predict_next_period(last_period_start, cycle_length=28):
    last_period_date = datetime.strptime(last_period_start, "%Y-%m-%d")
    next_period_date = last_period_date + timedelta(days=cycle_length)
    return next_period_date.strftime("%Y-%m-%d")

def plot_cycle_hormones(cycle_length=28):
    days = np.arange(1, cycle_length + 1)
    estrogen_levels = []
    progesterone_levels = []
    for day in days:
        estrogen, progesterone = hormone_levels(day, cycle_length)
        estrogen_levels.append(estrogen)
        progesterone_levels.append(progesterone)
    plt.figure(figsize=(10, 5))
    plt.plot(days, estrogen_levels, label="Estrogen Level", color="magenta")
    plt.plot(days, progesterone_levels, label="Progesterone Level", color="blue")
    plt.xlabel("Day of Cycle")
    plt.ylabel("Hormone Level")
    plt.title("Estrogen and Progesterone Levels Throughout Menstrual Cycle")
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    # Database setup
    create_table()

    # User Registration/Login
    action = input("Do you want to (register/login): ").strip().lower()
    username = input("Enter username: ")
    password = input("Enter password: ")

    if action == "register":
        register_user(username, password)
    elif action == "login":
        if not login_user(username, password):
            return
    else:
        print("Invalid action. Please choose 'register' or 'login'.")
        return

    # Menstrual Cycle Tracker Operations
    last_period_start = input("Enter the start date of your last period (YYYY-MM-DD): ")
    cycle_length = int(input("Enter your average cycle length in days: "))

    day = int(input(f"Enter a day (1-{cycle_length}) to check hormone levels: "))
    estrogen, progesterone = hormone_levels(day, cycle_length)
    print(f"On day {day} of your cycle:\n - Estrogen Level: {estrogen:.2f}\n - Progesterone Level: {progesterone:.2f}")

    ovulation_day, ovulation_window, estrogen_levels = predict_ovulation_phase(cycle_length)
    print(f"\nPredicted Ovulation Day: {ovulation_day}")
    print(f"Estimated Ovulation Window: Days {ovulation_window[0]} to {ovulation_window[1]}")

    next_period_start = predict_next_period(last_period_start, cycle_length)
    print(f"\nPredicted Next Period Start Date: {next_period_start}")

    plot_cycle_hormones(cycle_length)

if __name__ == "__main__":
    main()
    
