from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3
from datetime import datetime, timedelta
from astral import moon
from datetime import datetime
from astral.sun import sun

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

def get_moon_phase(date_str): #this function returns the moon phase based off a date paramater
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # astral 2.x returns 0-28 (roughly days of the lunar cycle)
    phase_value = moon.phase(date_obj)
    
    #return moon phase based off phase_value
    if phase_value < 1.0 or phase_value > 27.0:
        return "New Moon", 0
    elif phase_value < 6.0:
        return "Waxing Crescent", 25
    elif phase_value < 8.0:
        return "First Quarter", 50
    elif phase_value < 13.0:
        return "Waxing Gibbous", 75
    elif phase_value < 15.0:
        return "Full Moon", 100
    elif phase_value < 20.0:
        return "Waning Gibbous", 75
    elif phase_value < 22.0:
        return "Last Quarter", 50
    else:
        return "Waning Crescent", 25

def get_weather(location, target_date, target_time):
    """
    Searches the 5-day forecast for the 3-hour block closest to 
    the user's requested date and time.
    """
    try:
        # 1. Create a timestamp for the exact time the user wants
        target_datetime = datetime.strptime(f"{target_date} {target_time}", '%Y-%m-%d %H:%M')
        target_ts = target_datetime.timestamp()

        # 2. Fetch the 5-day/3-hour forecast data
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={API_KEY}"
        response = requests.get(url).json()
        if response.get('cod') != "200":
            return None

        # 3. Find the entry in the list with the timestamp closest to our target
        best_match = min(response['list'], key=lambda x: abs(x['dt'] - target_ts))
        
        # return weather conditions 
        return {
            'clouds': best_match['clouds']['all'],
            'description': best_match['weather'][0]['description'],
            'full_forecast': response['list'] # return the whole list to use for the 5-day forecast boxes later
        }
    except Exception as e:
        print(f"Weather Fetch Error: {e}")
        return None

@app.route('/results', methods=['POST'])
def results():
    '''
    Handles core stargazing calculation logic. 
    Processes user input, fetches real-time weather/astronomical data,
    calculates a 0-10 score, predicts conditions for next 5 days
    '''
    #get user inputs from home page form 
    user_location = request.form.get('location')
    user_date = request.form.get('date')
    user_time = request.form.get('time')

    # 1. Get moon phase for specific user-selected date
    moon_name, moon_brightness = get_moon_phase(user_date)

    # 2. Get weather data using our previous function
    weather_data = get_weather(user_location, user_date, user_time)

    #return to home if city not valid
    if not weather_data:
        return render_template('home.html', error="City not found or data unavailable!")

    clouds = weather_data['clouds']
    condition = weather_data['description']

    # 3. Calculate the Star Score (0-10)
    #start with a base of 10, penalize based on cloud percentage
    score = 10 - (clouds // 10)
    #remove points depending on how bright the moon is (bright moon washes out space objects)
    if moon_name == "Full Moon": 
        score -= 2
    elif "Gibbous" in moon_name:
        score -= 1
    #ensure score never drops below zero
    score = max(0, score)

    # 4. Save search results to SQLite database for the 'History' feature
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO searches (search_date, location, score) VALUES (?, ?, ?)",
                (user_date, user_location, score))
    conn.commit()
    conn.close()

    # 5. Seasonal Objects Logic: suggests things to look for based on Earth's position in orbit (month)
    month = datetime.strptime(user_date, '%Y-%m-%d').month
    if month in [12, 1, 2]:
        seasonal_objects = ["Orion Nebula", "Sirius (Brightest Star)", "The Pleiades"]
    elif month in [3, 4, 5]:
        seasonal_objects = ["Leo Constellation", "The Beehive Cluster", "Ursa Major"]
    elif month in [6, 7, 8]:
        seasonal_objects = ["The Milky Way Core", "Summer Triangle", "Saturn"]
    else:
        seasonal_objects = ["Andromeda Galaxy", "Pegasus Square", "Jupiter"]

    visible_objects = seasonal_objects
    #add moon to the list if it's currently visible
    if moon_name != "New Moon":
        visible_objects.append(f"{moon_name}")

    #6. 5-DAY PREDICTIVE FORECAST
    forecast_list = []
    raw_list = weather_data['full_forecast']
    
    for i in range(0, 40, 8): # jump by 8 to show the next 5 days
        day_data = raw_list[i]
        dt_obj = datetime.fromtimestamp(day_data['dt'])
        f_date = dt_obj.strftime('%Y-%m-%d')
        f_moon, _ = get_moon_phase(f_date)
        
        #calculate score using same logic
        f_clouds = day_data['clouds']['all']
        f_score = max(0, 10 - (f_clouds // 10) - (2 if f_moon == "Full Moon" else 1 if "Gibbous" in f_moon else 0))
        
        #add data to forecast_list to display, give "advice" based off calculated score
        forecast_list.append({
            "day": dt_obj.strftime('%a'),
            "score": f_score,
            "moon": f_moon,
            "advice": "Clear" if f_score >= 8 else "Visible" if f_score >= 5 else "Poor"
        })

    # 7. Pass everything to the results.html template
    return render_template('results.html', 
                            score=score, 
                            location=user_location, 
                            condition=condition, 
                            moon=moon_name,
                            objects=visible_objects,
                            forecast=forecast_list, 
                            search_date=user_date,   
                            search_time=user_time)

@app.route('/history')
def history():
    '''
    Retrives users search history from SQLite database.
    Displays results in newest-first order
    '''
    #connection to local database file
    conn = sqlite3.connect('database.db')

    # This row_factory makes the data easier to work with in HTML
    # allows us to access data by column name (e.g. search['location'])
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()
    
    # Get all searches, newest first
    cur.execute("SELECT * FROM searches ORDER BY id DESC")
    all_searches = cur.fetchall()
    conn.close()
    
    return render_template('history.html', searches=all_searches)

@app.route('/clear_history', methods=['POST'])
def clear_history(): #allows user to wipe their previous searches
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    # This deletes every row in the searches table
    cur.execute("DELETE FROM searches")
    conn.commit()
    conn.close()
    # After deleting, send the user back to the empty history page
    return redirect('/history')

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
