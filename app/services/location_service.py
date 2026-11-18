import math
from typing import Dict, Tuple, Optional, List

# City Database with approximate centroid coordinates and Tier status
CITIES_DB: Dict[str, Dict[str, any]] = {
    # Karnataka (Kannada focus)
    "bengaluru": {"name": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "tier": "Tier-1", "primary_lang": "kannada"},
    "bangalore": {"name": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "tier": "Tier-1", "primary_lang": "kannada"},
    "mysuru": {"name": "Mysuru", "state": "Karnataka", "lat": 12.2958, "lon": 76.6394, "tier": "Tier-2", "primary_lang": "kannada"},
    "mysore": {"name": "Mysuru", "state": "Karnataka", "lat": 12.2958, "lon": 76.6394, "tier": "Tier-2", "primary_lang": "kannada"},
    "hubballi": {"name": "Hubballi", "state": "Karnataka", "lat": 15.3647, "lon": 75.1240, "tier": "Tier-2", "primary_lang": "kannada"},
    "hubli": {"name": "Hubballi", "state": "Karnataka", "lat": 15.3647, "lon": 75.1240, "tier": "Tier-2", "primary_lang": "kannada"},
    "belagavi": {"name": "Belagavi", "state": "Karnataka", "lat": 15.8497, "lon": 74.4977, "tier": "Tier-2", "primary_lang": "kannada"},
    "mangaluru": {"name": "Mangaluru", "state": "Karnataka", "lat": 12.9141, "lon": 74.8560, "tier": "Tier-2", "primary_lang": "kannada"},
    "kalaburagi": {"name": "Kalaburagi", "state": "Karnataka", "lat": 17.3297, "lon": 76.8343, "tier": "Tier-2", "primary_lang": "kannada"},
    "davanagere": {"name": "Davanagere", "state": "Karnataka", "lat": 14.4644, "lon": 75.9218, "tier": "Tier-3", "primary_lang": "kannada"},
    "ballari": {"name": "Ballari", "state": "Karnataka", "lat": 15.1394, "lon": 76.9214, "tier": "Tier-3", "primary_lang": "kannada"},
    "shimoga": {"name": "Shivamogga", "state": "Karnataka", "lat": 13.9299, "lon": 75.5681, "tier": "Tier-3", "primary_lang": "kannada"},
    "shivamogga": {"name": "Shivamogga", "state": "Karnataka", "lat": 13.9299, "lon": 75.5681, "tier": "Tier-3", "primary_lang": "kannada"},
    "tumakuru": {"name": "Tumakuru", "state": "Karnataka", "lat": 13.3409, "lon": 77.1010, "tier": "Tier-3", "primary_lang": "kannada"},
    "udupi": {"name": "Udupi", "state": "Karnataka", "lat": 13.3409, "lon": 74.7421, "tier": "Tier-3", "primary_lang": "kannada"},
    "hassan": {"name": "Hassan", "state": "Karnataka", "lat": 13.0072, "lon": 76.1030, "tier": "Tier-3", "primary_lang": "kannada"},
    "mandya": {"name": "Mandya", "state": "Karnataka", "lat": 12.5222, "lon": 76.8978, "tier": "Tier-3", "primary_lang": "kannada"},
    "kolar": {"name": "Kolar", "state": "Karnataka", "lat": 13.1367, "lon": 78.1291, "tier": "Tier-3", "primary_lang": "kannada"},
    "chikkamagaluru": {"name": "Chikkamagaluru", "state": "Karnataka", "lat": 13.3161, "lon": 75.7720, "tier": "Tier-3", "primary_lang": "kannada"},
    "chitradurga": {"name": "Chitradurga", "state": "Karnataka", "lat": 14.2251, "lon": 76.3980, "tier": "Tier-3", "primary_lang": "kannada"},
    "vijayapura": {"name": "Vijayapura", "state": "Karnataka", "lat": 16.8302, "lon": 75.7100, "tier": "Tier-3", "primary_lang": "kannada"},
    "bijapur": {"name": "Vijayapura", "state": "Karnataka", "lat": 16.8302, "lon": 75.7100, "tier": "Tier-3", "primary_lang": "kannada"},
    "raichur": {"name": "Raichur", "state": "Karnataka", "lat": 16.2076, "lon": 77.3463, "tier": "Tier-3", "primary_lang": "kannada"},
    "bidar": {"name": "Bidar", "state": "Karnataka", "lat": 17.9104, "lon": 77.5199, "tier": "Tier-3", "primary_lang": "kannada"},
    "hosapete": {"name": "Hosapete", "state": "Karnataka", "lat": 15.2689, "lon": 76.3909, "tier": "Tier-3", "primary_lang": "kannada"},
    "gadag": {"name": "Gadag", "state": "Karnataka", "lat": 15.4167, "lon": 75.6333, "tier": "Tier-3", "primary_lang": "kannada"},
    "haveri": {"name": "Haveri", "state": "Karnataka", "lat": 14.7954, "lon": 75.3991, "tier": "Tier-3", "primary_lang": "kannada"},
    "bagalkote": {"name": "Bagalkote", "state": "Karnataka", "lat": 16.1875, "lon": 75.6980, "tier": "Tier-3", "primary_lang": "kannada"},
    "koppal": {"name": "Koppal", "state": "Karnataka", "lat": 15.3552, "lon": 76.1552, "tier": "Tier-3", "primary_lang": "kannada"},
    "yadgir": {"name": "Yadgir", "state": "Karnataka", "lat": 16.7628, "lon": 77.1378, "tier": "Tier-3", "primary_lang": "kannada"},
    "chamarajanagar": {"name": "Chamarajanagar", "state": "Karnataka", "lat": 11.9261, "lon": 76.9437, "tier": "Tier-3", "primary_lang": "kannada"},
    "ramanagara": {"name": "Ramanagara", "state": "Karnataka", "lat": 12.7209, "lon": 77.2799, "tier": "Tier-3", "primary_lang": "kannada"},
    "madikeri": {"name": "Madikeri", "state": "Karnataka", "lat": 12.4244, "lon": 75.7382, "tier": "Tier-3", "primary_lang": "kannada"},
    "kodagu": {"name": "Madikeri", "state": "Karnataka", "lat": 12.4244, "lon": 75.7382, "tier": "Tier-3", "primary_lang": "kannada"},

    # North / Central India (Hindi focus)
    "delhi": {"name": "Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.2090, "tier": "Tier-1", "primary_lang": "hindi"},
    "lucknow": {"name": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462, "tier": "Tier-2", "primary_lang": "hindi"},
    "kanpur": {"name": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lon": 80.3319, "tier": "Tier-2", "primary_lang": "hindi"},
    "patna": {"name": "Patna", "state": "Bihar", "lat": 25.5941, "lon": 85.1376, "tier": "Tier-2", "primary_lang": "hindi"},
    "varanasi": {"name": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739, "tier": "Tier-2", "primary_lang": "hindi"},
    "jaipur": {"name": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873, "tier": "Tier-2", "primary_lang": "hindi"},
    "indore": {"name": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577, "tier": "Tier-2", "primary_lang": "hindi"},
    "bhopal": {"name": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126, "tier": "Tier-2", "primary_lang": "hindi"},
    "ranchi": {"name": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lon": 85.3096, "tier": "Tier-2", "primary_lang": "hindi"},
    "agra": {"name": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lon": 78.0081, "tier": "Tier-2", "primary_lang": "hindi"},

    # Other Major Indian Metros
    "mumbai": {"name": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "tier": "Tier-1", "primary_lang": "hindi"},
    "hyderabad": {"name": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "tier": "Tier-1", "primary_lang": "hindi"},
}


class LocationService:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two geographic coordinates in kilometers.
        """
        r = 6371.0  # Earth's radius in kilometers
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 2)

    @staticmethod
    def resolve_city_coords(city_name: str) -> Tuple[float, float, str]:
        """
        Lookup city latitude, longitude, and tier. Supports any custom place, town, or village.
        """
        key = (city_name or "").strip().lower()
        if not key:
            return 12.9716, 77.5946, "Tier-2"

        if key in CITIES_DB:
            c = CITIES_DB[key]
            return c["lat"], c["lon"], c["tier"]

        # Partial substring match (e.g. "Hassan District", "South Bengaluru", etc.)
        for k, c in CITIES_DB.items():
            if k in key or key in k:
                return c["lat"], c["lon"], c["tier"]

        # Universal fallback for any custom town/village/place
        return 12.9716, 77.5946, "Tier-2"

    @staticmethod
    def get_city_info(city_name: str) -> Optional[Dict[str, any]]:
        key = (city_name or "").strip().lower()
        return CITIES_DB.get(key)

    @staticmethod
    def list_supported_cities() -> List[Dict[str, any]]:
        unique_cities = {}
        for k, v in CITIES_DB.items():
            if v["name"] not in unique_cities:
                unique_cities[v["name"]] = v
        return list(unique_cities.values())
