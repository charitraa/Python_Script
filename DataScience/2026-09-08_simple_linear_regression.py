"""
This script implements Simple Linear Regression from scratch without external libraries
like NumPy or scikit-learn.

It calculates the slope (m) and y-intercept (b) for a given set of (x, y) data points
using the least squares method. It also includes functions to make predictions and
evaluate the model's performance using the R-squared metric.

Simple Linear Regression aims to model the relationship between two continuous variables:
an independent variable (X) and a dependent variable (Y) by fitting a linear equation
of the form Y = mX + b to the observed data.
"""

def train_simple_linear_regression(x_data, y_data):
    """
    Trains a simple linear regression model to find the best-fit line (y = mx + b).

    Args:
        x_data (list): A list of independent variable (feature) values.
        y_data (list): A list of dependent variable (target) values, corresponding to x_data.

    Returns:
        tuple: A tuple containing the calculated slope (m) and y-intercept (b).
               Returns (None, None) if the data is insufficient or invalid.
    """
    if len(x_data) != len(y_data) or len(x_data) < 2:
        print("Error: x_data and y_data must have the same length and at least 2 points.")
        return None, None

    n = len(x_data)

    # Calculate means
    mean_x = sum(x_data) / n
    mean_y = sum(y_data) / n

    # Calculate the numerator and denominator for the slope (m)
    # The formula for slope (m) is:
    # m = sum((x_i - mean_x) * (y_i - mean_y)) / sum((x_i - mean_x)^2)
    numerator = 0
    denominator = 0
    for i in range(n):
        numerator += (x_data[i] - mean_x) * (y_data[i] - mean_y)
        denominator += (x_data[i] - mean_x) ** 2

    # Avoid division by zero if all x values are the same (no variance in X)
    if denominator == 0:
        print("Error: Cannot calculate slope. All x_data values are the same.")
        return None, None

    m = numerator / denominator
    
    # Calculate the y-intercept (b)
    # The formula for y-intercept (b) is:
    # b = mean_y - m * mean_x
    b = mean_y - m * mean_x

    return m, b

def predict(x_values, m, b):
    """
    Makes predictions using the trained simple linear regression model.

    Args:
        x_values (list): A list of x values for which to make predictions.
        m (float): The slope of the regression line.
        b (float): The y-intercept of the regression line.

    Returns:
        list: A list of predicted y values.
    """
    if m is None or b is None:
        print("Error: Model not trained or invalid slope/intercept provided for prediction.")
        return []
    
    predictions = [m * x + b for x in x_values]
    return predictions

def calculate_r_squared(y_true, y_predicted):
    """
    Calculates the R-squared (coefficient of determination) score.

    R-squared indicates how well the model fits the observed data.
    It is the proportion of the variance in the dependent variable that
    is predictable from the independent variable(s).
    R-squared ranges from 0 to 1, where 1 indicates a perfect fit.

    Args:
        y_true (list): A list of actual y values.
        y_predicted (list): A list of predicted y values from the model.

    Returns:
        float: The R-squared score, or None if data is insufficient or inconsistent.
    """
    if len(y_true) != len(y_predicted) or len(y_true) < 2:
        print("Error: y_true and y_predicted must have the same length and at least 2 points for R-squared.")
        return None

    n = len(y_true)
    mean_y_true = sum(y_true) / n

    # Total Sum of Squares (SS_tot)
    # SS_tot = sum((y_i - mean_y_true)^2)
    ss_total = sum([(y - mean_y_true) ** 2 for y in y_true])

    # Residual Sum of Squares (SS_res)
    # SS_res = sum((y_i - y_predicted_i)^2)
    ss_residual = sum([(y_true[i] - y_predicted[i]) ** 2 for i in range(n)])

    # Avoid division by zero if SS_total is 0 (all y_true values are the same)
    if ss_total == 0:
        print("Warning: All true y-values are the same. R-squared might not be meaningful.")
        # If all true y values are the same, and predictions also match this constant, it's a perfect fit (1.0).
        # Otherwise, if predictions vary, it's a poor fit (0.0).
        if ss_residual == 0:
            return 1.0
        return 0.0 # Bad fit if predictions don't match the constant true values

    # R-squared = 1 - (SS_res / SS_tot)
    r_squared = 1 - (ss_residual / ss_total)
    return r_squared

if __name__ == "__main__":
    print("--- Simple Linear Regression Example ---")

    # 1. Prepare some synthetic data
    # Let's aim for a relationship like y = 2 * x + 5, with some random noise.
    # Independent variable (e.g., hours studied)
    x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # Dependent variable (e.g., exam score)
    # These y_data points are chosen to approximately follow y = 2x + 5
    y_data = [7.1, 9.8, 11.2, 12.9, 15.3, 16.8, 18.7, 20.1, 22.0, 24.5] 

    print("\nTraining Data:")
    for i in range(len(x_data)):
        print(f"  X: {x_data[i]}, Y: {y_data[i]}")

    # 2. Train the model
    print("\nTraining the Simple Linear Regression model...")
    slope, intercept = train_simple_linear_regression(x_data, y_data)

    if slope is not None and intercept is not None:
        print(f"\nModel trained successfully!")
        print(f"  Calculated Slope (m): {slope:.4f}")
        print(f"  Calculated Y-intercept (b): {intercept:.4f}")
        print(f"  Regression Line Equation: Y = {slope:.4f} * X + {intercept:.4f}")

        # 3. Make predictions for new data points
        print("\nMaking predictions for new data points:")
        new_x_values = [0, 5.5, 12]
        predicted_y_values = predict(new_x_values, slope, intercept)

        for i in range(len(new_x_values)):
            print(f"  For X = {new_x_values[i]:.1f}, Predicted Y = {predicted_y_values[i]:.4f}")

        # 4. Evaluate the model using R-squared on the training data
        print("\nEvaluating model performance on training data:")
        y_predictions_on_train = predict(x_data, slope, intercept)
        r_squared_score = calculate_r_squared(y_data, y_predictions_on_train)

        if r_squared_score is not None:
            print(f"  R-squared (Coefficient of Determination): {r_squared_score:.4f}")
            print(f"  (R-squared explains the proportion of variance in Y predictable from X. Higher is better, max 1.0)")
        else:
            print("  Could not calculate R-squared score.")

    else:
        print("\nModel training failed due to data issues. Please check input data.")

    print("\n--- End of Example ---")
