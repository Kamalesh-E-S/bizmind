from flask import Blueprint, request, jsonify
from ..auth import auth_required
from ..google_maps import get_nearby_places, geocode_location, suggest_low_density_zones  # 👈 import new function
from ..utils import validate_location
from ..database import get_db
import json

heatmap_bp = Blueprint('heatmap', __name__)

@heatmap_bp.route('/heatmap')
@auth_required
def get_heatmap_data():
    location = request.args.get("location", "")
    category = request.args.get("category", "")
    user_id = request.user_id
    is_valid, error_msg = validate_location(location)
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    if not category:
        return jsonify({"error": "Category parameter is required"}), 400
    try:
        places_df, error = get_nearby_places(location, keyword=category)
        if error:
            return jsonify({"error": error}), 500
        coords, geocode_error = geocode_location(location)
        if geocode_error:
            return jsonify({"error": geocode_error}), 500
        response = {}
        if places_df.empty:
            response = {
                "coordinates": [],
                "center": coords,
                "count": 0
            }
        else:
            coordinates = places_df[['lat', 'lng']].to_dict('records')
            response = {
                "coordinates": coordinates,
                "center": coords,
                "count": len(coordinates)
            }
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO heatmap_data (user_id, location, category, heatmap_data) VALUES (?, ?, ?, ?)",
            (user_id, location, category, json.dumps(response))
        )
        db.commit()
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ New endpoint: suggest 5 low-density zones
@heatmap_bp.route('/suggest-locations')
@auth_required
def suggest_locations():
    """
    Suggest 5 coordinates where the selected store type has low density (ideal for new setup).
    """
    location = request.args.get("location", "")
    category = request.args.get("category", "")
    
    if not location or not category:
        return jsonify({"error": "Both 'location' and 'category' are required"}), 400

    is_valid, error_msg = validate_location(location)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    try:
        suggestions, error = suggest_low_density_zones(location, store_type=category)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({
            "base_location": location,
            "category": category,
            "suggested_zones": suggestions,
            "count": len(suggestions)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
