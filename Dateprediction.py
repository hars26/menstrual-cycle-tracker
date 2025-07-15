from datetime import datetime, timedelta

def predict_next_period(last_period_start, cycle_length=28):
    # Convert the last period start date from string to datetime
    last_period_date = datetime.strptime(last_period_start, "%Y-%m-%d")
    
    # Calculate the next period start date
    next_period_date = last_period_date + timedelta(days=cycle_length)
    
    # Format the result as a string for easy display
    next_period_start = next_period_date.strftime("%Y-%m-%d")
    
    print(f"Based on a {cycle_length}-day cycle, the next period is predicted to start on {next_period_start}.")
    return next_period_start

# Example usage:
last_period_start = "2024-10-01"  # Replace with actual last period date
cycle_length = 28  # Replace with user's average cycle length if different
predict_next_period(last_period_start, cycle_length)
