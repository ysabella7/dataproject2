import pandas as pd
import numpy as np
import plotly.express as px
from flask import Flask, render_template

# Set the file path
file_path = 'dirtydata.csv'

# Read the CSV file
data = pd.read_csv(file_path, encoding="windows-1252", na_values=['NaN', ''])

# Clean Data: Remove currency symbols, commas, duplicates, and missing values
data = data.replace({'€': '', ',': ''}, regex=True)
data.drop_duplicates(inplace=True)
data.dropna(inplace=True)

# Convert relevant columns to numeric
numeric_cols = ["corporation_tax", "capital_acq", "capital_gains", "employees_prsi", "vat"]
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors="coerce")

# Save cleaned data
cleaned_file_path = 'cleandata.csv'
data.to_csv(cleaned_file_path, index=False)
print("Cleaned data saved as:", cleaned_file_path)

# Compute statistics
non_numeric_cols = ['Year']
stats_dictionary = {}

for col in data.columns:
    if col not in non_numeric_cols:
        stats_data = data[col]
        stats_dictionary[col] = {
            'Mean': stats_data.mean(),
            'Median': stats_data.median(),
            'Mode': stats_data.mode().iloc[0] if not stats_data.mode().empty else np.nan,
            'Range': stats_data.max() - stats_data.min()
        }

stats_df = pd.DataFrame(stats_dictionary).transpose()
range_value = stats_df.loc["corporation_tax", "Range"]

# Recommendation Logic
if range_value > 10:
    recommendation = "That range is amazing. I'd recommend you optimize costs."
elif 1 < range_value <= 10:
    recommendation = "That range is great, but use your savings wisely."
else:
    recommendation = "Error: There may be possible data issues."

# Create Graphs with Plotly
data_long = data.melt(id_vars=["Year"], value_vars=["corporation_tax", "capital_gains"], var_name="Tax Type", value_name="Value")
bar_chart = px.bar(data_long, x="Year", y="Value", color="Tax Type", title="Corporation Tax vs Capital Gains Tax Over Time")
bar_chart_html = bar_chart.to_html(full_html=False, include_plotlyjs="cdn")

data_long = data.melt(id_vars=["Year"], value_vars=["corporation_tax", "capital_acq", "capital_gains", "employees_prsi", "vat"], var_name="Variable", value_name="Value")
line_chart = px.line(data_long, x="Year", y="Value", color="Variable", title="Tax Trends Over Time")
line_chart_html = line_chart.to_html(full_html=False, include_plotlyjs="cdn")

scatter_plot = px.scatter(data, x="capital_gains", y="employees_prsi", title="Capital Gains Tax vs Employees PRSI")
scatter_plot_html = scatter_plot.to_html(full_html=False, include_plotlyjs="cdn")

# Flask App
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', bar_chart=bar_chart_html, line_chart=line_chart_html, scatter_chart=scatter_plot_html)

@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html', recommendation=recommendation)

@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
