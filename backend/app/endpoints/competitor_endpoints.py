from flask import Blueprint, request, jsonify
from ..auth import auth_required
from ..google_maps import get_nearby_places
from ..utils import validate_location, dataframe_to_dict, format_json_response
from ..database import get_db
import json
from flask import Blueprint, request, jsonify, current_app
from ..auth import auth_required
from ..database import get_db
from ..groq_ai import call_groq_ai

competitor_bp = Blueprint('competitor', __name__)

# ...existing code...
@competitor_bp.route('/api/nearby-places', methods=['GET'])
@auth_required
def nearby_places():
    location = request.args.get('location')
    place_type = request.args.get('type')
    keyword = request.args.get('keyword')
    radius = request.args.get('radius', type=int)
    df, error = get_nearby_places(location, place_type, keyword, radius)
    if error:
        return jsonify({'error': error}), 400
    # Convert DataFrame to list of dicts for JSON response
    return jsonify(df.to_dict(orient='records'))
# ...existing code...
@competitor_bp.route('/competitor-insights')
@auth_required
def get_competitor_insights():
    location = request.args.get("location", "")
    category = request.args.get("category", "")
    user_id = request.user_id

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
            avg_rating = competitors_df['rating'].mean()
            avg_reviews = competitors_df['user_ratings_total'].mean()

            response = {
                "total": total,
                "avg_rating": round(float(avg_rating), 2),
                "avg_reviews": round(float(avg_reviews), 2),
                "details": dataframe_to_dict(competitors_df)
            }

        # --- Save to DB ---
        db = get_db()
        cursor = db.cursor()

        # Insert into main insights table
        cursor.execute("""
            INSERT INTO competitor_insights (user_id, location, category, total, avg_rating, avg_reviews)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, location, category, response["total"], response["avg_rating"], response["avg_reviews"]))

        insight_id = cursor.lastrowid

        # Insert each place (with summaries)
        for _, row in competitors_df.iterrows():
            summaries = row.get('summaries', {})
            cursor.execute("""
                INSERT INTO competitor_places (
                    insight_id, name, place_id, lat, lng, rating, user_ratings_total, vicinity, types,
                    positive_summary, negative_summary, positive_highlight, negative_highlight
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight_id,
                row.get('name'),
                row.get('place_id'),
                row.get('lat'),
                row.get('lng'),
                row.get('rating', 0),
                row.get('user_ratings_total', 0),
                row.get('vicinity'),
                json.dumps(row.get('types', [])),
                summaries.get('positive_summary'),
                summaries.get('negative_summary'),
                summaries.get('positive_highlight'),
                summaries.get('negative_highlight')
            ))

        db.commit()
        return jsonify(format_json_response(response))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/competitor-strategy', methods=['GET'])
@auth_required
def generate_business_strategy():
    """
    Fetch stored competitor summaries & highlights,
    send to LLM for generating strategic recommendations.
    """
    location = request.args.get("location", "")
    category = request.args.get("category", "")
    user_id = request.user_id

    if not location or not category:
        return jsonify({"error": "location and category are required"}), 400

    db = get_db()
    cursor = db.cursor()

    # Get the latest insight record for this user/location/category
    cursor.execute("""
        SELECT id FROM competitor_insights
        WHERE user_id = ? AND location = ? AND category = ?
        ORDER BY created_at DESC LIMIT 1
    """, (user_id, location, category))
    insight = cursor.fetchone()
    if not insight:
        return jsonify({"error": "No insights found. Please run competitor analysis first."}), 404

    insight_id = insight["id"]

    # Fetch all competitor places with summaries
    cursor.execute("""
        SELECT name, rating, user_ratings_total, 
               positive_summary, negative_summary,
               positive_highlight, negative_highlight
        FROM competitor_places
        WHERE insight_id = ?
    """, (insight_id,))
    competitors = cursor.fetchall()

    if not competitors:
        return jsonify({"error": "No competitor data found"}), 404

    # Combine data for AI prompt
    review_summary = []
    for c in competitors:
        review_summary.append({
            "name": c["name"],
            "rating": c["rating"],
            "reviews": c["user_ratings_total"],
            "pos_summary": c["positive_summary"],
            "neg_summary": c["negative_summary"],
            "pos_highlight": c["positive_highlight"],
            "neg_highlight": c["negative_highlight"]
        })

    # Build structured text for LLM
    prompt = f"""
You are an AI business strategist analyzing competitors for a new {category} business around {location}.

Below is competitor sentiment and highlights data extracted from Google Maps reviews:

{review_summary}

Using this data, generate a clear and actionable strategy that includes:
1. Key market gaps and opportunities.
2. What customers appreciate most (strengths).
3. What customers complain about (weaknesses).
4. 3–5 specific business strategies to outperform competitors.
5. Recommendations on marketing, service quality, pricing, or product differentiation.

Make it structured and concise.
"""

    try:
        llm_response = call_groq_ai(prompt)
        return jsonify({
            "strategy": llm_response,
            "context_used": review_summary
        })
    except Exception as e:
        return jsonify({"error": f"LLM processing failed: {str(e)}"}), 500

