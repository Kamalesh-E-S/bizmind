from flask import Blueprint, request, jsonify
from ..auth import auth_required
from ..google_maps import geocode_location, get_nearby_places
from ..utils import format_json_response, dataframe_to_dict
from ..database import get_db
import json
from flask import current_app
from ..groq_ai import call_groq_ai

strategy_bp = Blueprint('strategy', __name__)

def get_business_trends(location, radius=3000, user_id=None):
    import requests
    from collections import Counter
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    all_types = []
    business_relevant_types = {
        "restaurant", "cafe", "bar", "store", "clothing_store", "shopping_mall", "grocery_or_supermarket",
        "pharmacy", "bank", "atm", "beauty_salon", "hair_care", "car_repair", "gym", "spa", "electronics_store",
        "furniture_store", "pet_store", "hardware_store", "book_store", "shoe_store", "bakery", "laundry",
        "jewelry_store", "travel_agency", "insurance_agency", "real_estate_agency", "hospital", "doctor",
        "dentist", "physiotherapist", "veterinary_care"
    }
    params = {
        "location": location,
        "radius": radius,
        "type": "establishment",
        "key": current_app.config['GOOGLE_MAPS_API_KEY']
    }
    while True:
        response = requests.get(endpoint, params=params)
        data = response.json()
        for result in data.get("results", []):
            types = result.get("types", [])
            filtered = [t for t in types if t in business_relevant_types]
            all_types.extend(filtered)
        next_page_token = data.get("next_page_token")
        if next_page_token:
            import time
            time.sleep(2)
            params["pagetoken"] = next_page_token
        else:
            break
    from collections import Counter
    type_counts = Counter(all_types)
    if not type_counts:
        return {"error": "No relevant business data found in this location."}
    most_common = type_counts.most_common(5)
    least_common = sorted(type_counts.items(), key=lambda x: x[1])[:5]
    result = {
        "location": location,
        "top_categories": most_common,
        "untapped_categories": least_common
    }
    if user_id:
        try:
            db = get_db()
            cursor = db.cursor()
            try:
                coords, error = geocode_location(location)
                if not error:
                    gmaps = None
                    try:
                        import googlemaps
                        gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
                        reverse_geocode = gmaps.reverse_geocode((coords['lat'], coords['lng']))
                        location_name = reverse_geocode[0]['formatted_address'] if reverse_geocode else location
                    except Exception:
                        location_name = location
                else:
                    location_name = location
            except Exception:
                location_name = location
            cursor.execute(
                "INSERT OR REPLACE INTO analyzed_locations (user_id, location_coords, location_name, trend_data) VALUES (?, ?, ?, ?)",
                (user_id, location, location_name, json.dumps(result))
            )
            db.commit()
        except Exception as e:
            pass
    return result

def call_groq_for_strategy(business_type, location_name, location_coords, trend_data, competitor_data, user_id=None):
    user_context = ""
    if user_id:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT business_name FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user and user['business_name']:
            user_context = f"For the business '{user['business_name']}', "
    trend_summary = "No trend data available."
    if trend_data:
        top_categories = ", ".join([f"{cat} ({count} instances)" for cat, count in trend_data.get("top_categories", [])])
        untapped = ", ".join([f"{cat} ({count} instances)" for cat, count in trend_data.get("untapped_categories", [])])
        trend_summary = f"Top business categories in the area: {top_categories}. Untapped opportunities: {untapped}."
    competitor_summary = "No competitor data available."
    if competitor_data:
        total = competitor_data.get("total", 0)
        avg_rating = competitor_data.get("avg_rating", 0)
        avg_reviews = competitor_data.get("avg_reviews", 0)
        competitor_summary = f"There are {total} similar businesses with average rating of {avg_rating}/5 and {avg_reviews} reviews on average."
    prompt = f"""
    {user_context}I'm planning to open a {business_type} business in {location_name} (coordinates: {location_coords}).\n\nLocal market data:\n{trend_summary}\n\nCompetitor analysis:\n{competitor_summary}\n\nPlease provide:\n1. A business strategy recommendation (3 key points)\n2. Suggested unique selling proposition\n3. Target customer demographic\n4. One innovative location-specific marketing idea\n    """
    return call_groq_ai(prompt, system_message="You are a business strategy expert who provides concise, actionable advice.")

def generate_business_strategy(location_name, location_coords, business_type, user_id, trend_data=None, competitor_data=None):
    strategy = call_groq_for_strategy(
        business_type,
        location_name,
        location_coords,
        trend_data,
        competitor_data,
        user_id
    )
    db = get_db()
    cursor = db.cursor()
    trend_data_json = json.dumps(trend_data) if trend_data else None
    competitor_data_json = json.dumps(competitor_data) if competitor_data else None
    cursor.execute('''
        INSERT INTO business_strategies 
        (user_id, business_type, location_name, location_coords, trend_data, competitor_data, strategy)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, business_type, location_name, location_coords, trend_data_json, competitor_data_json, strategy))
    db.commit()
    strategy_id = cursor.lastrowid
    return {
        "strategy_id": strategy_id,
        "business_type": business_type,
        "location": location_name,
        "strategy": strategy
    }

@strategy_bp.route('/generate-strategy', methods=['POST'])
@auth_required
def strategy_generator_endpoint():
    data = request.get_json()
    user_id = request.user_id
    location = data.get("location")
    business_type = data.get("business_type")
    if not location:
        return jsonify({"error": "Location parameter is required"}), 400
    if not business_type:
        return jsonify({"error": "Business type parameter is required"}), 400
    try:
        coords, error = geocode_location(location)
        if error:
            return jsonify({"error": error}), 400
        location_coords = f"{coords['lat']},{coords['lng']}"
        try:
            import googlemaps
            gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
            reverse_geocode = gmaps.reverse_geocode((coords['lat'], coords['lng']))
            location_name = reverse_geocode[0]['formatted_address'] if reverse_geocode else location
        except Exception:
            location_name = location
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM analyzed_locations WHERE user_id = ? AND location_coords = ?", (user_id, location_coords))
        existing_location = cursor.fetchone()
        if existing_location and existing_location['trend_data']:
            trend_data = json.loads(existing_location['trend_data'])
        else:
            trend_data = get_business_trends(location_coords, user_id=user_id)
        competitors_df, error = get_nearby_places(location, keyword=business_type)
        if error:
            competitor_data = {"error": error}
        else:
            total = len(competitors_df) if not competitors_df.empty else 0
            avg_rating = competitors_df['rating'].mean() if not competitors_df.empty and 'rating' in competitors_df.columns else 0
            avg_reviews = competitors_df['user_ratings_total'].mean() if not competitors_df.empty and 'user_ratings_total' in competitors_df.columns else 0
            competitor_data = {
                "total": total,
                "avg_rating": round(float(avg_rating), 2) if avg_rating else 0,
                "avg_reviews": round(float(avg_reviews), 2) if avg_reviews else 0,
                "details": dataframe_to_dict(competitors_df) if not competitors_df.empty else []
            }
            cursor.execute(
                "INSERT INTO competitor_insights (user_id, location, category, insight_data) VALUES (?, ?, ?, ?)",
                (user_id, location, business_type, json.dumps(competitor_data))
            )
            db.commit()
        strategy_result = generate_business_strategy(
            location_name,
            location_coords,
            business_type,
            user_id,
            trend_data,
            competitor_data
        )
        response = {
            "location": {
                "name": location_name,
                "coordinates": coords
            },
            "business_type": business_type,
            "trends": trend_data,
            "competitors": competitor_data,
            "strategy": strategy_result
        }
        return jsonify(format_json_response(response))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@strategy_bp.route('/strategies', methods=['GET'])
@auth_required
def list_strategies():
    try:
        user_id = request.user_id
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM business_strategies WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        strategies = []
        for row in cursor.fetchall():
            strategy_dict = dict(row)
            if strategy_dict.get('trend_data'):
                strategy_dict['trend_data'] = json.loads(strategy_dict['trend_data'])
            if strategy_dict.get('competitor_data'):
                strategy_dict['competitor_data'] = json.loads(strategy_dict['competitor_data'])
            strategies.append(strategy_dict)
        return jsonify({
            "total": len(strategies),
            "strategies": strategies
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@strategy_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
@auth_required
def get_strategy(strategy_id):
    try:
        user_id = request.user_id
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM business_strategies WHERE id = ? AND user_id = ?", (strategy_id, user_id))
        strategy = cursor.fetchone()
        if not strategy:
            return jsonify({"error": "Strategy not found or unauthorized"}), 404
        strategy_dict = dict(strategy)
        if strategy_dict.get('trend_data'):
            strategy_dict['trend_data'] = json.loads(strategy_dict['trend_data'])
        if strategy_dict.get('competitor_data'):
            strategy_dict['competitor_data'] = json.loads(strategy_dict['competitor_data'])
        return jsonify(strategy_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
