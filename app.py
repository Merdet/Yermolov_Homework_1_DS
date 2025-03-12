from flask import Flask, request, jsonify
import requests
from datetime import date, datetime, timezone
import openai
from collections import OrderedDict
import json


app = Flask(__name__)

SECURITY_KEY = "Homework_Yermolov"
VISUAL_CROSSING_API_KEY = "AQ4DPKXELWQTZN99MGGHWAY6D"
OPENAI_API_KEY = "your_openai_api_key"
BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

def check_security_token():
    token = request.headers.get("Authorization")
    return token == SECURITY_KEY

def ask_chatgpt(conditions, temperature):
    prompt = (f"The weather forecast is {conditions} with a temperature of {temperature}°C. "
              "Should I take an umbrella? Provide a detailed response explaining your recommendation.")
    
    client = openai.OpenAI(api_key="OpenAI_API")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

@app.route('/weather', methods=['GET'])
def get_weather():
    if not check_security_token():
        return jsonify({"error": "Unauthorized"}), 401

    timestamp = datetime.now(timezone.utc)
    current_date = date.today()
    location = request.args.get('location', 'New York')
    start_date = request.args.get("start_date", str(current_date))
    end_date = request.args.get("end_date", start_date)
    unit_group = request.args.get('unitGroup', 'metric')  
    requester_name = request.args.get('requester_name', 'Unknown')
    
    url = f"{BASE_URL}/{location}/{start_date}/{end_date}?unitGroup={unit_group}&key={VISUAL_CROSSING_API_KEY}&contentType=json"
    
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch weather data"}), 500
        
        weather_data = []
        
        for day in data["days"]:
            conditions = day["conditions"]
            temperature = day["temp"]
            wind_kph = day.get("windspeed", 0)
            pressure_mb = day.get("pressure", 0)
            umbrella_advice = ask_chatgpt(conditions, temperature)
            
            weather_data.append(OrderedDict([
                ("date", day["datetime"]),
                ("temperature", temperature),
                ("conditions", conditions),
                ("humidity", day["humidity"]),
                ("wind_kph", wind_kph),
                ("pressure_mb", pressure_mb),
                ("umbrella_advice", umbrella_advice)
                ]))
        
        ordered_response = OrderedDict([
            ("timestamp", timestamp.isoformat()),
            ("requester_name", requester_name),
            ("location", location),
            ("date", str(current_date)),
            ("weather_data", weather_data),
            ])

        return app.response_class(
            response=json.dumps(ordered_response, ensure_ascii=False, indent=4, sort_keys=False),
            mimetype="application/json"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
