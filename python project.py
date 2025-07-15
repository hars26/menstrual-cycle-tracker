from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

def hormone_levels(day, cycle_length=28):
    """Calculate estrogen and progesterone levels for a given day in the cycle."""
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
    """Predict ovulation phase and return the window with peak estrogen levels."""
    ovulation_day = cycle_length // 2
    ovulation_window = (ovulation_day - 2, ovulation_day + 2)
    
    max_estrogen = 200
    min_estrogen = 50
    estrogen_levels = [min_estrogen + (max_estrogen - min_estrogen) * np.sin(np.pi * day / cycle_length) for day in range(1, cycle_length + 1)]
    
    return ovulation_day, ovulation_window, estrogen_levels

def predict_next_period(last_period_start, cycle_length=28):
    """Predict the start date of the next period based on last period start date."""
    last_period_date = datetime.strptime(last_period_start, "%Y-%m-%d")
    next_period_date = last_period_date + timedelta(days=cycle_length)
    return next_period_date.strftime("%Y-%m-%d")

def plot_cycle_hormones(cycle_length=28):
    """Generate and display a plot of hormone levels throughout the cycle."""
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
    # Gather user input
    last_period_start = input("Enter the start date of your last period (YYYY-MM-DD): ")
    cycle_length = int(input("Enter your average cycle length in days: "))

    # Calculate and display hormone levels
    day = int(input(f"Enter a day (1-{cycle_length}) to check hormone levels: "))
    estrogen, progesterone = hormone_levels(day, cycle_length)
    print(f"On day {day} of your cycle:\n - Estrogen Level: {estrogen:.2f}\n - Progesterone Level: {progesterone:.2f}")

    # Predict ovulation phase
    ovulation_day, ovulation_window, estrogen_levels = predict_ovulation_phase(cycle_length)
    print(f"\nPredicted Ovulation Day: {ovulation_day}")
    print(f"Estimated Ovulation Window: Days {ovulation_window[0]} to {ovulation_window[1]}")

    # Predict next period start date
    next_period_start = predict_next_period(last_period_start, cycle_length)
    print(f"\nPredicted Next Period Start Date: {next_period_start}")

    # Display full cycle hormone levels plot
    plot_cycle_hormones(cycle_length)

if __name__ == "__main__":
    main()
