# StarGuide: An Intelligent Stargazing Planner
StarGuide is a comprehensive web application designed to help astronomy enthusiasts determine the perfect time to observe the night sky. By merging real-time weather data with astronomical lunar tracking, the application provides users with a clear, actionable "Star Score" for any location.

### Special Features:
* **Stargazing Algorithm:** The core of the project is a custom scoring algorithm that analyzes multiple environmental factors. It checks for rain, cloud cover pecentages, and moon phases to create a stargazing score based off the user's date, time, and location. For instance, even a clear night receives a lower score if a Full Moon is creating significant natural light pollution, which is critical for deep-space observation.
* **Time-Based Data:** The application does not simply pull "current" weather. It implements an algorithm that finds and displays the meteorological conditions closest to the user's specific requested observation time.
* **Moon Phase Tracking:** Using the `astral` library, the program automatically calculates the lunar cycle for the next five days. It identifies eight distinct phases (from New Moon to Waning Gibbous), providing users with information on how the moon's brightness will impact their visibility.
* **5-Day Forecast:** The application leverages the OpenWeather 5-Day/3-Hour API. The logic checks weather forecasts for night times, allowing users to plan their trips up to a week in advance.
* **Search History:** Integrated with a SQLite3 database, the app features a "Past Searches" module. This allows users to track historical conditions and quickly revisit their most-searched locations without re-typing coordinates.
* **Professional UX/UI Design:** The interface features clean design elements, a mobile-responsive centered layout, and color-coding. High scores appear in vibrant green, while poor conditions are highlighted in red, providing an immediate visually-pleasing style status update at a glance. A clean, dark night sky background remains throughout the pages. 

### Technical Stuff
* **Backend:** Python & Flask
* **Database:** SQLite3
* **APIs:** OpenWeather Geocoding & 5-Day Forecast
* **Libraries:** Requests, Astral, Jinja2
* **Frontend:** HTML5, CSS3 