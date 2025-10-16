# Creates line chart comparing spending on lobbying by interests representing the funeral home industry and cemetery industry 
# in Massachusetts based on lobbying disclosure reports between 2015 and 2024
# Data is embedded in script. 

import pandas as pd
import matplotlib.pyplot as plt
import io
import matplotlib.ticker as mticker

# --- Data Embedded in Script ---
# The CSV data is now stored in a multi-line string.
data = """Year,Yearth Funeral Group Inc.,Massachusetts Funeral Directors Association,Affiliated Family Funeral Service Inc.,Massachusetts Cemetery Association,Proprietors of the Cemetery of Mount Auburn,Total
"2025(*Jan-June)",22911,41000,3750,9000,36610,113271
2024,0,92166,0,18000,60000,172190
2023,0,58000,0,16000,60910,136933
2022,0,28000,0,12000,54750,96772
2021,0,28678,0,12000,0,42699
2020,0,14428,0,12000,0,28448
2019,0,14000,0,12000,0,28019
2018,0,10000,0,12000,0,24018
2017,0,14000,0,12000,0,28017
2016,0,14000,0,12000,0,28016
2015,0,14000,0,12000,0,28015
"""

# Load the data from the string into a pandas DataFrame
df = pd.read_csv(io.StringIO(data))


# --- Data Cleaning and Preparation ---

# Clean the 'Year' column to handle "2025(*Jan-June)"
df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})').astype(int)

# Filter the DataFrame to include data from 2017 to 2024
df = df[(df['Year'] >= 2017) & (df['Year'] <= 2024)]

# Define the groups
funeral_groups = [
    'Yearth Funeral Group Inc.',
    'Massachusetts Funeral Directors Association',
    'Affiliated Family Funeral Service Inc.'
]
cemetery_groups = [
    'Massachusetts Cemetery Association',
    'Proprietors of the Cemetery of Mount Auburn'
]

# Calculate the total spending for each group
df['Funeral Group Spending'] = df[funeral_groups].sum(axis=1)
df['Cemetery Group Spending'] = df[cemetery_groups].sum(axis=1)

# Keep only the year and the aggregate spending columns
df_agg = df[['Year', 'Funeral Group Spending', 'Cemetery Group Spending']].set_index('Year')
df_agg = df_agg.sort_index() # Sort by year ascending

# --- Matplotlib Chart Generation ---

# Adjust figsize for a portrait orientation
fig, ax = plt.subplots(figsize=(8, 10))

# Define colors
colors = {
    'Funeral Group Spending': 'blue',
    'Cemetery Group Spending': 'red'
}

# Plot each line
for column, color in colors.items():
    ax.plot(df_agg.index, df_agg[column], marker='o', linestyle='-', color=color, label=column)

# --- Formatting the Plot ---

# Set title and labels
ax.set_title('Lobbying Spending by Funeral vs. Cemetery Groups per Year', fontsize=16)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Total Spending ($)', fontsize=12)

# Rotate x-axis labels for better fit on portrait screens
plt.xticks(rotation=45, ha='right')

# Format the y-axis to show dollar signs and commas
formatter = mticker.FormatStrFormatter('$%1.0f')
ax.yaxis.set_major_formatter(formatter)

# Set the upper limit of the y-axis
ax.set_ylim(top=100000)

# Add a legend
ax.legend(title='')

# Add grid for better readability
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
ax.set_facecolor('white') # Set background to white

# Ensure the plot layout is tight
plt.tight_layout()

# Save the plot as a PNG image file
plt.savefig('spending_over_time_portrait.png', dpi=300)

print("The line chart has been generated and saved as 'spending_over_time_portrait.png'.")
