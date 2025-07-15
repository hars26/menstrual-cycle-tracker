import numpy as np

def predict_ovulation_phase(cycle_length=28):
    """
    Predicts the ovulation phase based on the length of the menstrual cycle.
    Default is set to 28 days but can be adjusted for other cycle lengths.
    """
    # Average ovulation phase is approximately the midpoint of the cycle
    ovulation_day = cycle_length // 2
    ovulation_window_start = ovulation_day - 2
    ovulation_window_end = ovulation_day + 2

    # Hormone fluctuations to indicate the ovulation phase
    max_estrogen = 200
    min_estrogen = 50
    estrogen_levels = [
        min_estrogen + (max_estrogen - min_estrogen) * np.sin(np.pi * day / cycle_length)
        for day in range(1, cycle_length + 1)
    ]

    print(f"Predicted Ovulation Phase: Days {ovulation_window_start}-{ovulation_window_end}")
    print("Peak Estrogen Levels (indicator of ovulation):")
    
    for day in range(ovulation_window_start, ovulation_window_end + 1):
        print(f"Day {day}: Estrogen Level ~ {estrogen_levels[day - 1]:.2f}")

    return {
        "ovulation_day": ovulation_day,
        "ovulation_window": (ovulation_window_start, ovulation_window_end),
        "peak_estrogen_levels": [estrogen_levels[day - 1] for day in range(ovulation_window_start, ovulation_window_end + 1)]
    }

# Predict ovulation phase for a 28-day cycle
ovulation_info = predict_ovulation_phase()
