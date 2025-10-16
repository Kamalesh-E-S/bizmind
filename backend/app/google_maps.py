import googlemaps
import pandas as pd
from flask import current_app
import time
from textblob import TextBlob
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from textblob import TextBlob
from collections import Counter
import re

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
        
def summarize_for_llm(reviews, sentiment_type="positive"):
    """
    Create ultra-compact summary and highlight line for any business.
    Works for restaurants, shops, clinics, etc.
    """
    if not reviews:
        return "", ""

    # Combine review text
    full_text = " ".join([r["text"] for r in reviews])

    # Tokenize & clean
    words = re.findall(r'\b\w+\b', full_text.lower())
    stopwords = {
        "the","and","for","was","very","had","with","but","are","this","that",
        "were","also","at","in","on","a","of","to","is","it","we","as","from",
        "they","you","be","an","by","so","if","or","not"
    }
    filtered = [w for w in words if w not in stopwords and len(w) > 2]

    if not filtered:
        return "", ""

    # Common keywords
    common = [w for w, _ in Counter(filtered).most_common(10)]

    # Aspect flags
    aspects = {
        "food": any(x in common for x in ["food","taste","dish","menu","meal","biryani"]),
        "service": any(x in common for x in ["service","staff","delivery","waiter","behavior","attitude"]),
        "price": any(x in common for x in ["price","cost","expensive","cheap","worth","value"]),
        "ambience": any(x in common for x in ["ambience","place","atmosphere","clean","decor","environment"]),
        "quality": any(x in common for x in ["quality","product","item","experience","value"]),
        "time": any(x in common for x in ["delay","waiting","late","quick","fast"])
    }

    icons = {
        "food": "🍽️", "service": "🤝", "price": "💰",
        "ambience": "✨", "quality": "✅", "time": "⏱️"
    }
    highlights = " ".join([icons[k] for k,v in aspects.items() if v])

    # Avg sentiment
    avg_sentiment = sum(r["sentiment"] for r in reviews) / len(reviews)

    # Compact one-liner summary for LLM input
    compact_summary = (
        f"{sentiment_type.upper()} → S:{avg_sentiment:+.2f} | "
        f"A:{highlights or '—'} | "
        f"K:{', '.join(common[:6])}"
    )

    # Highlight (natural-language single line)
    if sentiment_type == "positive":
        highlight = f"Customers mostly praised the {', '.join([k for k,v in aspects.items() if v]) or 'overall experience'}."
    else:
        highlight = f"Customers mainly complained about the {', '.join([k for k,v in aspects.items() if v]) or 'service quality'}."

    return compact_summary.strip(), highlight.strip()

def get_place_reviews(place_id):
    """
    Fetch up to 5 'good' and 'bad' reviews, analyze sentiment, and create summaries + highlights.
    """
    gmaps = get_gmaps_client()
    try:
        details = gmaps.place(place_id=place_id, fields=["reviews", "name"])
        result = details.get("result", {})
        reviews = result.get("reviews", [])

        if not reviews:
            return [], [], {}

        analyzed_reviews = []
        for r in reviews:
            text = r.get("text", "").strip()
            if not text:
                continue
            sentiment = TextBlob(text).sentiment.polarity
            analyzed_reviews.append({
                "author": r.get("author_name"),
                "rating": r.get("rating"),
                "text": text,
                "sentiment": sentiment,
                "time": r.get("time")
            })

        if not analyzed_reviews:
            return [], [], {}

        sorted_positive = sorted(analyzed_reviews, key=lambda r: r["sentiment"], reverse=True)
        sorted_negative = sorted(analyzed_reviews, key=lambda r: r["sentiment"])

        top_reviews = sorted_positive[:5]
        least_reviews = sorted_negative[:5]

        pos_summary, pos_highlight = summarize_for_llm(top_reviews, "positive")
        neg_summary, neg_highlight = summarize_for_llm(least_reviews, "negative")

        summaries = {
            "positive_summary": pos_summary,
            "negative_summary": neg_summary,
            "positive_highlight": pos_highlight,
            "negative_highlight": neg_highlight
        }

        return top_reviews, least_reviews, summaries

    except Exception as e:
        import logging
        logging.error(f"Error fetching reviews for {place_id}: {e}")
        return [], [], {}

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
            top_reviews, least_reviews, summaries = get_place_reviews(place_id)
            # print("Good reviews summary:", summaries["positive_summary"],"\n",summaries["positive_highlight"])
            # print("Bad reviews summary:", summaries["negative_summary"],"\n",summaries["negative_highlight"])
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
                'least_reviews': least_reviews,
                'summaries': summaries
            })
            # Sleep to avoid hitting rate limits
            time.sleep(0.2)

        return pd.DataFrame(places) if places else pd.DataFrame(), None

    except Exception as e:
        return None, f"Google Places API error: {str(e)}"

import math
from geopy.distance import geodesic

def suggest_low_density_zones(location, store_type, radius=5000, grid_step=1000):
    """
    Suggests up to 5 coordinates (circles) near a location where a given store type is less present.
    
    Args:
        location (str): Location name or "lat,lng"
        store_type (str): Type of place to check (e.g., 'restaurant', 'gym')
        radius (int): Search radius in meters around the base location
        grid_step (int): Distance (in meters) between grid points to sample

    Returns:
        list of dict: Suggested low-density zones with coords and nearby area names
    """
    gmaps = get_gmaps_client()
    coords, error = geocode_location(location)
    if error:
        return None, error

    lat, lng = coords['lat'], coords['lng']
    R = 6371000  # Earth radius (m)
    
    sample_points = []
    for dlat in range(-radius, radius + 1, grid_step):
        for dlng in range(-radius, radius + 1, grid_step):
            new_lat = lat + (dlat / R) * (180 / math.pi)
            new_lng = lng + (dlng / R) * (180 / math.pi) / math.cos(lat * math.pi / 180)
            sample_points.append((new_lat, new_lng))

    density_map = []
    for (lat_s, lng_s) in sample_points:
        try:
            places_result = gmaps.places_nearby(
                location=(lat_s, lng_s),
                radius=800,  # check density around point
                type=store_type
            )
            count = len(places_result.get("results", []))
            density_map.append({
                "lat": lat_s,
                "lng": lng_s,
                "count": count
            })
            time.sleep(0.2)
        except Exception:
            continue

    # Sort by least number of existing stores
    low_density = sorted(density_map, key=lambda x: x["count"])[:5]

    # Reverse geocode for names
    suggestions = []
    for zone in low_density:
        try:
            rev = gmaps.reverse_geocode((zone["lat"], zone["lng"]))
            zone_name = rev[0]["formatted_address"] if rev else "Unknown area"
        except Exception:
            zone_name = "Unknown area"

        suggestions.append({
            "lat": round(zone["lat"], 6),
            "lng": round(zone["lng"], 6),
            "existing_stores_nearby": zone["count"],
            "suggested_area": zone_name
        })

    return suggestions, None

