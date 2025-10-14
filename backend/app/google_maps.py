import googlemaps
import pandas as pd
from flask import current_app

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

def get_nearby_places(location, place_type=None, keyword=None, radius=None):
    gmaps = get_gmaps_client()
    coords, error = geocode_location(location)
    if error:
        return None, error
    try:
        places_result = gmaps.places_nearby(
            location=(coords['lat'], coords['lng']),
            radius=radius or current_app.config['MAPS_RADIUS'],
            type=place_type,
            keyword=keyword
        )
        places = []
        for place in places_result.get('results', []):
            places.append({
                'name': place.get('name'),
                'place_id': place.get('place_id'),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'rating': place.get('rating', 0),
                'user_ratings_total': place.get('user_ratings_total', 0),
                'vicinity': place.get('vicinity'),
                'types': place.get('types', [])
            })
        return pd.DataFrame(places) if places else pd.DataFrame(), None
    except Exception as e:
        return None, f"Google Places API error: {str(e)}"
