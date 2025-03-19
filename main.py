import os
import pandas as pd
import numpy as np
import plotly.express as px
from flask import Flask, render_template

# Flask app
app = Flask(__name__, template_folder="templates")

# set the file path to the templates folder
#file_path = 'dirtydata.csv'
file_path = os.path.join(app.template_folder, 'dirtydata.csv')

# read the file using pandas
data = pd.read_csv(file_path, encoding="windows-1252", na_values=['NaN', ''])
# print(data.columns)
# print("Column names in DataFrame:", data.columns.tolist())

# if encoding is not working, use encoding='utf-8'

# read the file using pandas and remove special characters (€)
#data = pd.read.csv(file_path)
data = data.replace({'€': '', ',': ''}, regex=True)


# remove any duplicate rows
data.drop_duplicates(inplace=True)

# drop and delete rows with missing data
data = data.dropna()

# fill this in
numeric_cols = ["corporation_tax", "capital_acq", "capital_gains", "employees_prsi", "vat"]
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors="coerce")  # Convert to numbers

# save cleaned data to a new file
cleaned_file_path = 'cleandata.csv'

data.to_csv(cleaned_file_path, index = False)

print("I saved the clean file here:", cleaned_file_path)

# print(data["corporation_tax"].unique())  # See unique values in the column


# define non numeric columns 
non_numeric_cols = ['Year']

# create a dictionary for statistics
stats_dictionary = {}

for col in data.columns: # go through each column but skip first column
  if col not in non_numeric_cols:
    stats_data = data[col]
    # populate stats_dictionary with stats on each column 
    stats_dictionary[col] = {
      'Mean': stats_data.mean(),
      'Median': stats_data.median(),
      'Mode': stats_data.mode().iloc[0] if not stats_data.mode().empty else np.nan,
      'Range': stats_data.max() - stats_data.min()
    }

# to view the dictionary 
# print(stats_dictionary)

# convert stats to DataFrame
stats_df = pd.DataFrame(stats_dictionary).transpose()
print(stats_df)

# print(data.columns)

range_value = stats_df.loc["corporation_tax", "Range"]
print("My range is: ", range_value)

# recommend based on range
if range_value > 10:
    recommendation = "That range is amazing. I'd recommend you optimize costs."
elif 1 < range_value <= 10:
    recommendation = "That range is great, but use your savings wisely."
else:
    recommendation = "Error: There may be possible data issues."

# create graphs with Plotly
data_long = data.melt(id_vars=["Year"],
                      value_vars=["corporation_tax", "capital_gains"],
                      var_name="Tax Type", value_name="Value")

bar_chart = px.bar(data_long,
                   x="Year",
                   y="Value",
                   color="Tax Type",
                   title="Corporation Tax vs Capital Gains Tax Over Time")

bar_chart_html = bar_chart.to_html(full_html=False, include_plotlyjs=True)

data_long = data.melt(id_vars=["Year"],
                      value_vars=["corporation_tax", "capital_acq", "capital_gains", "employees_prsi", "vat"],
                      var_name="Variable",
                      value_name="Value")

line_chart = px.line(data_long,
                     x="Year",
                     y="Value",
                     color="Variable",
                     title="Tax Trends Over Time")

line_chart_html = line_chart.to_html(full_html=False, include_plotlyjs=True)

scatter_plot = px.scatter(data,
                          x="capital_gains",
                          y="employees_prsi",
                          color="Year",        # use 'Year' for colouring
                          title="Capital Gains Tax vs Employees PRSI by Year")

scatter_plot_html = scatter_plot.to_html(full_html=False, include_plotlyjs=True)


@app.route('/')
def index():
    print(f'Bar Chart: {bar_chart_html}')
    print(f'Line Chart: {line_chart_html}')
    print(f'Scatter Chart: {scatter_plot_html}')
    return render_template('index.html', bar_chart=bar_chart_html, line_chart=line_chart_html, scatter_chart=scatter_plot_html)

@app.route('/recommendations')
def recommendations():
    print(f'Recommendation: {recommendation}')
    return render_template('recommendations.html', recommendation=recommendation)

@app.route('/suggestions')
def suggestions():
    #suggestion = "Suggestion"
    print(f'Suggestions: {suggestion}')
    return render_template('suggestions.html', suggestion=suggestion)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5002, debug=True)
    #app.run(host='127.0.0.1', port=5001, debug=False)
    #app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
