# Define the function computepay
def computepay(hours, rate):
    if hours > 40:
        regular_pay = 40 * rate
        overtime_pay = (hours - 40) * (rate * 1.5)
        total_pay = regular_pay + overtime_pay
    else:
        total_pay = hours * rate
    return total_pay

# Input values
hours = float(input("Enter Hours: "))
rate = float(input("Enter Rate: "))

# Compute the pay
pay = computepay(hours, rate)

# Output the result
print("Pay:", pay)
