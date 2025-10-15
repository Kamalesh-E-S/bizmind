from flask import Blueprint, request, jsonify
from ..auth import auth_required
from ..google_maps import get_nearby_places
from ..utils import validate_location, dataframe_to_dict, format_json_response
from ..database import get_db
import json

competitor_bp = Blueprint('competitor', __name__)

@competitor_bp.route('/competitor-insights')
@auth_required
def get_competitor_insights():
    location = request.args.get("location", "")
    category = request.args.get("category", "")
    user_id = request.user_id

    # Input validation
    is_valid, error_msg = validate_location(location)
    if not is_valid:
        return jsonify({"error": error_msg}), 400
    if not category:
        return jsonify({"error": "Category parameter is required"}), 400

    try:
        competitors_df, error = get_nearby_places(location, keyword=category)
        if error:
            return jsonify({"error": error}), 500

        if competitors_df.empty:
            response = {
                "total": 0,
                "avg_rating": 0,
                "avg_reviews": 0,
                "details": []
            }
        else:
            total = len(competitors_df)
            avg_rating = competitors_df['rating'].mean() if 'rating' in competitors_df.columns else 0
            avg_reviews = competitors_df['user_ratings_total'].mean() if 'user_ratings_total' in competitors_df.columns else 0

            # Convert DataFrame to JSON-safe format
            details = dataframe_to_dict(competitors_df)
            response = {
                "total": total,
                "avg_rating": round(float(avg_rating), 2),
                "avg_reviews": round(float(avg_reviews), 2),
                "details": details
            }

        # Save in DB
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO competitor_insights (user_id, location, category, insight_data) VALUES (?, ?, ?, ?)",
            (user_id, location, category, json.dumps(response))
        )
        db.commit()

        return jsonify(format_json_response(response))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
