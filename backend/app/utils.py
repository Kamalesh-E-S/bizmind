import json
from datetime import datetime
from flask import request
import pandas as pd

def log_request(req, log_file):
    timestamp = datetime.now().isoformat()
    client_host = request.remote_addr or "unknown"
    params = dict(request.args)
    log_data = {
        "timestamp": timestamp,
        "method": request.method,
        "url": request.url,
        "path": request.path,
        "params": params,
        "client_ip": client_host,
        "user_agent": request.headers.get("user-agent", "unknown")
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(log_data) + "\n")

def validate_location(location: str):
    if not location:
        return False, "Location parameter is required"
    if "," in location:
        try:
            lat, lng = location.split(",")
            float(lat.strip())
            float(lng.strip())
            return True, "Valid location"
        except ValueError:
            pass
    return True, "Valid location"

def format_json_response(data):
    return json.loads(json.dumps(data, default=str))

def dataframe_to_dict(df):
    if isinstance(df, pd.DataFrame):
        return df.to_dict(orient="records")
    return df
