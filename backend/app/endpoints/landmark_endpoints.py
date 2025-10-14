from flask import Blueprint, request, jsonify
from ..auth import auth_required
from ..database import get_db
import requests
import json

landmark_bp = Blueprint('landmark', __name__)

def search_nearby(location, place_type, api_key):
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": 3000,
        "type": place_type,
        "key": api_key
    }
    response = requests.get(endpoint, params=params)
    return response.json().get("results", [])

from flask import current_app
from ..groq_ai import call_groq_ai

@landmark_bp.route('/landmark-mapper', methods=['POST'])
@auth_required
def landmark_mapper():
    data = request.get_json()
    business = data.get("business")
    base_location = data.get("location")
    user_id = request.user_id
    if not business:
        return jsonify({"error": "Please provide a business type or name"}), 400
    api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    hostels = search_nearby(base_location, "lodging", api_key)
    schools = search_nearby(base_location, "school", api_key)
    apartments = search_nearby(base_location, "apartment", api_key)
    landmark_data = {
        "hostels": [h["name"] for h in hostels[:5]],
        "schools": [s["name"] for s in schools[:5]],
        "apartments": [a["name"] for a in apartments[:5]]
    }
    user_context = ""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT business_name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user and user['business_name']:
        user_context = f"For the business '{user['business_name']}', "
    prompt = f"""
    {user_context}I am opening a new business: '{business}'.\nBased on the nearby landmarks data: {landmark_data},\nsuggest the best location (lat/lng) where customer footfall is likely to be highest.\nReturn only the coordinates and a short explanation.
    """
    ai_response = call_groq_ai(prompt, system_message="You are a helpful business advisor with geospatial reasoning.")
    cursor.execute(
        "INSERT INTO landmark_data (user_id, business, location, landmark_data, recommendation) VALUES (?, ?, ?, ?, ?)",
        (user_id, business, base_location, json.dumps(landmark_data), ai_response)
    )
    db.commit()
    return jsonify({
        "business": business,
        "base_location": base_location,
        "landmarks_analyzed": landmark_data,
        "recommended_location": ai_response
    })
