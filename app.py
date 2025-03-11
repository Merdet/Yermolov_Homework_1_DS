from flask import Flask, request, jsonify
import requests
from datetime import date, timedelta, datetime, timezone
app = Flask(__name__)

SECURITY_KEY = "Homework_Yermolov"

VISUAL_CROSSING_API_KEY = "AQ4DPKXELWQTZN99MGGHWAY6D"

BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

def check_security_token():
    token = request.headers.get("Authorization")
    return token == SECURITY_KEY


@app.route('/weather', methods=['GET'])
def get_weather():
    if not check_security_token():
        return jsonify({"error": "Unauthorized"}), 401
    timestamp = datetime.now(timezone.utc)
    current_date = date.today()
    location = request.args.get('location', 'New York')
    start_date = request.args.get("start_date", str(current_date))
    end_date = request.args.get("end_date", str(current_date + timedelta(days=7)))
    unit_group = request.args.get('unitGroup', 'metric')  # metric або us
    requester_name = request.args.get('requester_name', 'Unknown')
    
    url = f"{BASE_URL}/{location}/{start_date}/{end_date}?unitGroup={unit_group}&key={VISUAL_CROSSING_API_KEY}&contentType=json"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch weather data"}), 500
        weather_data = [
            {
                "date": day["datetime"],
                "temperature": day["temp"],
                "conditions": day["conditions"],
                "humidity": day["humidity"],
                "wind_speed": day["windspeed"]
            } for day in data["days"]
            ]
        return jsonify({
            "timestamp": timestamp,
            "requester_name": requester_name,
            "location": location,
            "date": str(current_date),
            "weather_data": weather_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)