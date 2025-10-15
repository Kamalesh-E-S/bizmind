import googlemaps
import pandas as pd
from flask import current_app
import time

def get_gmaps_client():
    return googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])

def geocode_location(location):
    gmaps = get_gmaps_client()
    if "," in location:
        try:
            lat, lng = location.split(",")
            return {"lat": float(lat.strip()), "lng": float(lng.strip())}, None
        except ValueError:
            pass
    try:
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            return None, "Location not found"
        location_coords = geocode_result[0]['geometry']['location']
        return location_coords, None
    except Exception as e:
        return None, f"Geocoding error: {str(e)}"

def get_place_reviews(place_id):
    """
    Fetch up to 5 reviews from the Google Places Details API for a specific place.
    Returns both highest-rated and lowest-rated reviews sorted by rating.
    """
    gmaps = get_gmaps_client()
    try:
        details = gmaps.place(place_id=place_id, fields=["reviews", "name"])
        reviews = details.get("result", {}).get("reviews", [])

        if not reviews:
            return [], []

        # Sort reviews by rating descending for top, ascending for least
        sorted_reviews_desc = sorted(reviews, key=lambda r: r.get("rating", 0), reverse=True)
        sorted_reviews_asc = sorted(reviews, key=lambda r: r.get("rating", 0))

        top_reviews = [
            {
                "author": r.get("author_name"),
                "rating": r.get("rating"),
                "text": r.get("text"),
                "time": r.get("time")
            }
            for r in sorted_reviews_desc[:5]
        ]
        least_reviews = [
            {
                "author": r.get("author_name"),
                "rating": r.get("rating"),
                "text": r.get("text"),
                "time": r.get("time")
            }
            for r in sorted_reviews_asc[:5]
        ]
        return top_reviews, least_reviews

    except Exception as e:
        return [], []

def get_nearby_places(location, place_type=None, keyword=None, radius=None):
    gmaps = get_gmaps_client()
    coords, error = geocode_location(location)
    if error:
        return None, error

    try:
        places_result = gmaps.places_nearby(
            location=(coords['lat'], coords['lng']),
            radius=radius or current_app.config.get('MAPS_RADIUS', 2000),
            type=place_type,
            keyword=keyword
        )

        places = []
        for place in places_result.get('results', []):
            place_id = place.get('place_id')
            top_reviews, least_reviews = get_place_reviews(place_id)
            places.append({
                'name': place.get('name'),
                'place_id': place_id,
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'rating': place.get('rating', 0),
                'user_ratings_total': place.get('user_ratings_total', 0),
                'vicinity': place.get('vicinity'),
                'types': place.get('types', []),
                'top_reviews': top_reviews,
                'least_reviews': least_reviews
            })
            # Sleep to avoid hitting rate limits
            time.sleep(0.2)

        return pd.DataFrame(places) if places else pd.DataFrame(), None

    except Exception as e:
        return None, f"Google Places API error: {str(e)}"
