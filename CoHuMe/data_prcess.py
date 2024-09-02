import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data for each dataset
datasets = [
    {
        'datafile': 'Final-V2_200_3.csv',
        'title': 'Dataset 1',
        'color': 'blue',
        'range_percent': 0.05
    },

]

plt.figure(figsize=(12, 8))

# Process and plot each dataset on the same plot
for dataset in datasets:
    # Load data
    data = pd.read_csv(dataset['datafile'])

    # Assuming the columns are unnamed, you can refer to them by index
    x = data.iloc[:, 0].values  # Assuming the first column is x
    y = data.iloc[:, 1].values  # Assuming the second column is y

    # Determine the number of points to select (top 10%)
    num_points = int(len(y) * 0.1)

    # Sort indices based on y-values in descending order and select top 10%
    sorted_indices = np.argsort(y)[::-1][:num_points]

    # Use the selected points for fitting
    x_selected = x[sorted_indices]
    y_selected = y[sorted_indices]

    # Fit a 10th order polynomial to the selected points
    coefficients = np.polyfit(x_selected, y_selected, 10)
    poly = np.poly1d(coefficients)

    # Find the peak of the polynomial
    x_peak = x_selected[np.argmax(poly(x_selected))]

    # Determine the range around the peak to plot the polynomial
    x_range_min = x_peak - (dataset['range_percent'] * (max(x_selected) - min(x_selected)))
    x_range_max = x_peak + (dataset['range_percent'] * (max(x_selected) - min(x_selected)))

    # Generate x values for plotting the polynomial within the specified range
    x_range = np.linspace(x_range_min, x_range_max, 1000)

    # Plot the data and polynomial on the same plot
    plt.scatter(x, y, label=f'{dataset["title"]} - All Data Points', color=dataset['color'], alpha=0.6)
    plt.scatter(x_selected, y_selected, color=dataset['color'], marker='o', label=f'{dataset["title"]} - Top 10% Points')

    # Plot the polynomial within the specified range
    plt.plot(x_range, poly(x_range), color=dataset['color'], linestyle='-', linewidth=2,
             label=f'{dataset["title"]} - 10th Order Polynomial')

    # Mark the peak on the plot
    plt.scatter(x_peak, poly(x_peak), color='black', marker='x', s=100,
                label=f'{dataset["title"]} - Peak at x={x_peak:.2f}, y={poly(x_peak):.2f}')

plt.title('10th Order Polynomial Fit to Top 10% Highest Points')
plt.xlabel('Vo (V)')
plt.ylabel('Frequency (GHz)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
