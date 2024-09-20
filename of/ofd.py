from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta


app = Flask(__name__,  static_folder='static')

# Dummy user credentials for validation
app.secret_key = 'your_secret_key'  # Required for session management
users = {'admin': 'admin'}

# Load the dataset
df = pd.read_excel("D:\\of\\Dataset\\indian_restaurant_sales.xlsx")

# Preprocess the data
df['Date'] = pd.to_datetime(df['Date'])

# Add Order Count for forecasting
df['Order Count'] = df.groupby(['Date', 'Item Name'])['Customer ID'].transform('nunique')

# Define helper functions
def forecast_demand(item_name, periods=7):
    # Filter data for the specific item
    item_data = df[df['Item Name'] == item_name].copy()
    
    # Resample the data to daily frequency and aggregate
    daily_data = item_data.set_index('Date').resample('D').agg({
        'Order Count': 'sum',
        'Quantity Ordered': 'sum'
    }).fillna(0)
    
    # Prepare the features (X) and targets (y) for forecasting
    daily_data['DayOfWeek'] = daily_data.index.dayofweek
    
    X = daily_data[['DayOfWeek']]
    y_orders = daily_data['Order Count']
    y_quantity = daily_data['Quantity Ordered']
    
    # Split the data into training and testing sets
    X_train, X_test, y_orders_train, y_orders_test, y_quantity_train, y_quantity_test = train_test_split(
        X, y_orders, y_quantity, test_size=0.2, random_state=42)
    
    # Train the decision tree regressor for orders
    model_orders = DecisionTreeRegressor(random_state=42)
    model_orders.fit(X_train, y_orders_train)
    
    # Train the decision tree regressor for quantity
    model_quantity = DecisionTreeRegressor(random_state=42)
    model_quantity.fit(X_train, y_quantity_train)
    
    # Create a DataFrame for the next 7 days
    forecast_dates = [daily_data.index.max() + timedelta(days=i) for i in range(1, periods + 1)]
    forecast_days = [date.dayofweek for date in forecast_dates]
    X_forecast = pd.DataFrame({'DayOfWeek': forecast_days})
    
    # Forecast orders and quantity
    forecast_orders = model_orders.predict(X_forecast).round().astype(int)
    forecast_quantity = model_quantity.predict(X_forecast).round().astype(int)
    
    # Avoid zeros: if forecast is zero, use historical average
    historical_avg_orders = daily_data['Order Count'].mean()
    historical_avg_quantity = daily_data['Quantity Ordered'].mean()
    
    forecast_orders[forecast_orders == 0] = max(1, round(historical_avg_orders))
    forecast_quantity[forecast_quantity == 0] = max(1, round(historical_avg_quantity))
    
    forecast_quantity_series = pd.Series(forecast_quantity, index=forecast_dates)
    forecast_orders_series = pd.Series(forecast_orders, index=forecast_dates)
    
    return forecast_quantity_series, forecast_orders_series

def dynamic_pricing():
    average_sales = df.groupby('Item Name')['Quantity Ordered'].mean()
    top_6_products = average_sales.nlargest(6).index
    least_5_products = average_sales.nsmallest(5).index

    prices = []
    for item in df['Item Name'].unique():
        base_price = df[df['Item Name'] == item]['Price of Single Quantity'].mean()
        if item in top_6_products:
            suggested_price = round(base_price * 1.05)
        elif item in least_5_products:
            suggested_price = round(base_price * 0.96)
        else:
            suggested_price = round(base_price)
        prices.append({'Item Name': item, 'Base Price': round(base_price), 'Suggested Price': suggested_price})
    return prices

# Login Route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        
        # Check if the credentials are correct
        if userid == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials. Please try again.')
            return render_template('verify.html')
    return render_template('verify.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Debug print to check form data
        print(request.form)

        # Check if 'mobile_number' exists in the form data
        restaurant_name = request.form.get('restaurant_name')
        location = request.form.get('location')
        mobile_number = request.form.get('mobile_number')
        email = request.form.get('email')

        # Validate that all fields are present
        if not mobile_number:
            flash('Mobile number is required.')
            return render_template('signup.html')

        # Handle saving the restaurant details here (to database, file, etc.)
        flash(f'Signup successful for {restaurant_name}!')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Route for homepage after login
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    total_customers = df['Customer ID'].nunique()
    total_orders = df.shape[0]
    total_revenue = df['Total Price'].sum()
    
    # Get the top 10 most visited customers
    top_customers = df.groupby('Customer ID').size().nlargest(10).reset_index(name='Number of Visits')
    
    return render_template('index.html', 
                           total_customers=total_customers, 
                           total_orders=total_orders, 
                           total_revenue=round(total_revenue, 2),
                           top_customers=top_customers)

# Logout route
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/forecast')
def forecast():
    items = df['Item Name'].unique()
    forecasts = {}
    fixed_dates = pd.date_range(start="2024-07-01", end="2024-07-07")

    for item in items:
        forecast_quantity, forecast_orders = forecast_demand(item)
        
        forecast_data = pd.DataFrame({
            'Date': fixed_dates,
            'Forecast Quantity': forecast_quantity.reindex(fixed_dates, method='ffill').fillna(0).astype(int),
            'Forecast Orders': forecast_orders.reindex(fixed_dates, method='ffill').fillna(0).astype(int)
        })
        
        forecasts[item] = forecast_data.values.tolist()

    return render_template('forecast.html', forecasts=forecasts)

@app.route('/dynamic_pricing')
def dynamic_pricing_route():
    prices = dynamic_pricing()
    return render_template('dynamic_pricing.html', prices=prices)

@app.route('/patterns')
def patterns():
    patterns = df.groupby(['Gender', 'Customer Occupation', 'Item Name']).size().unstack(fill_value=0).idxmax(axis=1)
    return render_template('patterns.html', patterns=patterns)

@app.route('/sales_ratio')
def sales_ratio_route():
    veg_sales = df[df['Item Category'] == 'veg']['Total Price'].sum()
    non_veg_sales = df[df['Item Category'] == 'non-veg']['Total Price'].sum()
    total_sales = veg_sales + non_veg_sales
    veg_ratio = round(veg_sales / total_sales, 2)
    non_veg_ratio = round(non_veg_sales / total_sales, 2)
    return render_template('sales_ratio.html', veg_ratio=veg_ratio, non_veg_ratio=non_veg_ratio)

@app.route('/revenue')
def revenue():
    total_sales = df.set_index('Date').resample('D').sum()['Total Price']
    model = DecisionTreeRegressor()
    X = total_sales.index.dayofweek.values.reshape(-1, 1)  # Use day of the week as a feature
    y = total_sales.values
    
    model.fit(X, y)
    future_days = np.array([day % 7 for day in range(X[-1][0] + 1, X[-1][0] + 8)]).reshape(-1, 1)
    revenue_forecast = model.predict(future_days)
    
    return render_template('revenue.html', revenue_forecast=round(revenue_forecast.sum(), 2))

@app.route('/most_demanded')
def most_demanded():
    # Get the top 5 most demanded food items
    top_5_demanded_items = df.groupby('Item Name')['Quantity Ordered'].sum().nlargest(5).reset_index()
    return render_template('most_demanded.html', top_5_demanded_items=top_5_demanded_items)

@app.route('/visualizations')
def visualizations():
    return render_template('visualizations.html')

if __name__ == '__main__':
    app.run(debug=True)
