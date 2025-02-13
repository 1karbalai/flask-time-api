from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from config import API_KEY

app = Flask(__name__)

# Läs in länder och tidszoner från CSV
df = pd.read_csv("countries.csv")

# Start-sidan (webbsidan)
@app.route("/")
def home():
    countries = df["country"].tolist()  # Lista med länder för dropdown-menyn
    return render_template("index.html", countries=countries)

# API-endpoint för att hämta tid
@app.route("/get_time", methods=["GET"])
def get_country_time():
    country = request.args.get("country")

    if not country:
        return jsonify({"error": "Ange ett land!"}), 400

    row = df[df["country"].str.lower() == country.lower()]
    if row.empty:
        return jsonify({"error": "Landet finns inte i databasen!"}), 404

    timezone = row.iloc[0]["timezone"]

    # Hämta aktuell tid från TimeZoneDB
    try:
        url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={API_KEY}&format=json&by=zone&zone={timezone}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        current_time = data.get("formatted", "Tid ej tillgänglig")
    except requests.exceptions.RequestException as e:
        current_time = "Fel vid hämtning av tid"

    return jsonify({"country": country, "timezone": timezone, "current_time": current_time})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
