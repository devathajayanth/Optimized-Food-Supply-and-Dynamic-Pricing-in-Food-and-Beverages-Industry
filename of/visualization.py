import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter

# Load the dataset
file_path = 'D:\\of\\Dataset\\indian_restaurant_sales.xlsx'
df = pd.read_excel(file_path)

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Function to save plots
def save_plot(fig, filename):
    fig.savefig(f'D:\\of\\image\\{filename}', bbox_inches='tight')

# Time series analysis for each item
item_sales = df.groupby(['Date', 'Item Name']).agg({'Quantity Ordered': 'sum'}).reset_index()

# Individual time series analysis for each item
unique_items = df['Item Name'].unique()
for item in unique_items:
    item_data = item_sales[item_sales['Item Name'] == item]
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(item_data['Date'], item_data['Quantity Ordered'], label=item, marker='o')
    ax.set_title(f'Time Series Analysis of {item}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Quantity Ordered')
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    plt.grid(True)
    save_plot(fig, f'time_series_{item}.png')

# Combined time series analysis for all items
fig, ax = plt.subplots(figsize=(14, 7))
for item in unique_items:
    item_data = item_sales[item_sales['Item Name'] == item]
    ax.plot(item_data['Date'], item_data['Quantity Ordered'], label=item)

ax.set_title('Time Series Analysis of Each Food Item')
ax.set_xlabel('Date')
ax.set_ylabel('Quantity Ordered')
ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.xticks(rotation=45)
plt.grid(True)
save_plot(fig, 'time_series_analysis.png')  # Saved as time_series_analysis.png

# Veg vs Non-Veg sales in a pie chart
veg_nonveg_sales = df.groupby('Item Category').agg({'Total Price': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(veg_nonveg_sales['Total Price'], labels=veg_nonveg_sales['Item Category'], autopct='%1.1f%%', startangle=140)
ax.set_title('Veg vs Non-Veg Sales')
save_plot(fig, 'veg_nonveg_pie_chart.png')  # Saved as veg_nonveg_pie_chart.png

# Bar charts for all food item sales
item_total_sales = df.groupby('Item Name').agg({'Total Price': 'sum'}).reset_index().sort_values(by='Total Price', ascending=False)
fig, ax = plt.subplots(figsize=(14, 7))
sns.barplot(x='Total Price', y='Item Name', data=item_total_sales, palette='viridis')
ax.set_title('Total Sales for Each Food Item')
ax.set_xlabel('Total Sales')
ax.set_ylabel('Food Item')
save_plot(fig, 'total_sales_each_item.png')  # Saved as total_sales_each_item.png

# Additional visualizations

# Sales over time
sales_over_time = df.groupby('Date').agg({'Total Price': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(sales_over_time['Date'], sales_over_time['Total Price'], color='blue')
ax.set_title('Total Sales Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Total Sales')
ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
plt.xticks(rotation=45)
plt.grid(True)
save_plot(fig, 'sales_over_time.png')  # Saved as sales_over_time.png

# Quantity ordered by item type
item_type_quantity = df.groupby('Item Type').agg({'Quantity Ordered': 'sum'}).reset_index().sort_values(by='Quantity Ordered', ascending=False)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='Quantity Ordered', y='Item Type', data=item_type_quantity, palette='coolwarm')
ax.set_title('Quantity Ordered by Item Type')
ax.set_xlabel('Quantity Ordered')
ax.set_ylabel('Item Type')
save_plot(fig, 'quantity_ordered_item_type.png')  # Saved as quantity_ordered_item_type.png

# Average price per item
average_price_item = df.groupby('Item Name').agg({'Price of Single Quantity': 'mean'}).reset_index().sort_values(by='Price of Single Quantity', ascending=False)
fig, ax = plt.subplots(figsize=(14, 7))
sns.barplot(x='Price of Single Quantity', y='Item Name', data=average_price_item, palette='inferno')
ax.set_title('Average Price per Item')
ax.set_xlabel('Average Price')
ax.set_ylabel('Food Item')
save_plot(fig, 'average_price_per_item.png')  # Saved as average_price_per_item.png

# Sales by Customer Gender
gender_sales = df.groupby('Gender').agg({'Total Price': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x='Gender', y='Total Price', data=gender_sales, palette='muted')
ax.set_title('Total Sales by Customer Gender')
ax.set_xlabel('Gender')
ax.set_ylabel('Total Sales')
save_plot(fig, 'sales_by_gender.png')  # Saved as sales_by_gender.png

# Sales by Time of Day
time_of_day_sales = df.groupby('Time of Order').agg({'Total Price': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='Time of Order', y='Total Price', data=time_of_day_sales, palette='cool')
ax.set_title('Total Sales by Time of Day')
ax.set_xlabel('Time of Day')
ax.set_ylabel('Total Sales')
save_plot(fig, 'sales_by_time_of_day.png')  # Saved as sales_by_time_of_day.png

# Sales by Customer Occupation
occupation_sales = df.groupby('Customer Occupation').agg({'Total Price': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='Total Price', y='Customer Occupation', data=occupation_sales, palette='Spectral')
ax.set_title('Total Sales by Customer Occupation')
ax.set_xlabel('Total Sales')
ax.set_ylabel('Customer Occupation')
save_plot(fig, 'sales_by_occupation.png')  # Saved as sales_by_occupation.png

# Total Sales by Weekday
df['Weekday'] = df['Date'].dt.day_name()
weekday_sales = df.groupby('Weekday').agg({'Total Price': 'sum'}).reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='Weekday', y='Total Price', data=weekday_sales, palette='Paired')
ax.set_title('Total Sales by Weekday')
ax.set_xlabel('Weekday')
ax.set_ylabel('Total Sales')
save_plot(fig, 'sales_by_weekday.png')  # Saved as sales_by_weekday.png

# Heatmap of Sales by Item and Day of the Week
heatmap_data = df.pivot_table(values='Total Price', index='Item Name', columns='Weekday', aggfunc='sum').fillna(0)
fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(heatmap_data, cmap='YlGnBu', ax=ax)
ax.set_title('Heatmap of Sales by Item and Day of the Week')
save_plot(fig, 'sales_heatmap.png')  # Saved as sales_heatmap.png


