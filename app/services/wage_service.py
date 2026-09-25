from typing import Dict, Any, Optional
from app.services.location_service import LocationService

# Standard base daily wage benchmarks (8-hour workday, Tier-2 baseline in INR)
TRADE_BASE_RATES: Dict[str, Dict[str, Any]] = {
    "helper": {"name": "General Helper / Labour", "base": 550.0, "category": "Unskilled", "kn": "ಕೂಲಿ ಕಾರ್ಮಿಕ", "hi": "मजदूर / सहायक"},
    "loader": {"name": "Loading & Shifting", "base": 600.0, "category": "Unskilled", "kn": "ಹಮಾಲಿ", "hi": "पल्लेदार / लोडर"},
    "painter": {"name": "Painter", "base": 750.0, "category": "Semi-skilled", "kn": "ಪೇಂಟರ್", "hi": "पेंटर"},
    "gardener": {"name": "Gardener", "base": 650.0, "category": "Semi-skilled", "kn": "ತೋಟಗಾರ", "hi": "माली"},
    "plumber": {"name": "Plumber", "base": 850.0, "category": "Skilled", "kn": "ಪ್ಲಂಬರ್", "hi": "प्लंबर"},
    "carpenter": {"name": "Carpenter", "base": 900.0, "category": "Skilled", "kn": "ಬಡಗಿ", "hi": "बढ़ई"},
    "electrician": {"name": "Electrician", "base": 900.0, "category": "Skilled", "kn": "ಎಲೆಕ್ಟ್ರಿಷಿಯನ್", "hi": "इलेक्ट्रीशियन"},
    "mason": {"name": "Mason / Mestri", "base": 950.0, "category": "Skilled", "kn": "ಮೇಸ್ತ್ರಿ", "hi": "राजमिस्त्री"},
    "welder": {"name": "Welder / Fabricator", "base": 950.0, "category": "Skilled", "kn": "ವೆಲ್ಡರ್", "hi": "वेल्डर"},
    "tile_mason": {"name": "Tiles / Flooring Mason", "base": 1000.0, "category": "High-skilled", "kn": "ಟೈಲ್ಸ್ ಮೇಸ್ತ್ರಿ", "hi": "टाइल मिस्त्री"},
    "ac_technician": {"name": "AC / Appliance Tech", "base": 1050.0, "category": "High-skilled", "kn": "ಎಸಿ ಮೆಕ್ಯಾನಿಕ್", "hi": "एसी तकनीशियन"},
    "driver": {"name": "Commercial Driver", "base": 800.0, "category": "Semi-skilled", "kn": "ಚಾಲಕ", "hi": "चालक / ड्राइवर"}
}

TIER_MULTIPLIERS = {
    "Tier-1": 1.25,  # Metros: Bengaluru, Delhi, Mumbai
    "Tier-2": 1.00,  # Hubballi, Mysuru, Lucknow, Patna
    "Tier-3": 0.85   # Davanagere, Ballari, Tumakuru, smaller towns
}


class FairWageService:
    @staticmethod
    def get_trade_key(trade_name: str) -> str:
        t = (trade_name or "").strip().lower().replace(" ", "_")
        for key in TRADE_BASE_RATES:
            if key in t or t in key:
                return key
        return "helper"

    @classmethod
    def predict_fair_wage(
        cls,
        trade: str,
        city: str,
        experience_years: int = 3,
        has_own_tools: bool = True,
        is_urgent: bool = False,
        hours_per_day: int = 8,
        wage_offered: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates the recommended fair daily & hourly wage using market heuristics,
        city economic tier, experience compounding, and tool compensation.
        """
        trade_key = cls.get_trade_key(trade)
        trade_meta = TRADE_BASE_RATES[trade_key]
        base_rate = trade_meta["base"]

        # City tier lookup
        _, _, city_tier = LocationService.resolve_city_coords(city)
        tier_multiplier = TIER_MULTIPLIERS.get(city_tier, 1.0)

        # Experience increment: +3% per year up to 15 years
        exp_clamped = min(max(experience_years, 0), 15)
        exp_multiplier = 1.0 + (exp_clamped * 0.03)

        # Tool ownership premium: +₹100 to ₹180 depending on skill
        tool_premium = 0.0
        if has_own_tools:
            tool_premium = 150.0 if trade_meta["category"] in ("Skilled", "High-skilled") else 80.0

        # Urgency premium: +20% for immediate emergency jobs
        urgency_multiplier = 1.20 if is_urgent else 1.0

        # Calculation
        calculated_daily = (base_rate * tier_multiplier * exp_multiplier * urgency_multiplier) + tool_premium
        # Round to nearest ₹50
        recommended_daily = round(calculated_daily / 50.0) * 50.0

        # Min and Max fair wage band
        min_fair_wage = round((recommended_daily * 0.85) / 50.0) * 50.0
        max_fair_wage = round((recommended_daily * 1.25) / 50.0) * 50.0

        hourly_wage = round(recommended_daily / max(hours_per_day, 1), 1)

        # Evaluate fairness bracket
        wage_bracket = "FAIR"
        if wage_offered is not None and wage_offered > 0:
            if wage_offered < min_fair_wage:
                wage_bracket = "BELOW_FAIR_WAGE"
            elif wage_offered > max_fair_wage:
                wage_bracket = "PREMIUM_OFFER"
            else:
                wage_bracket = "FAIR_MARKET_RATE"

        # Multi-lingual regional explanations
        trade_kn = trade_meta.get("kn", trade)
        trade_hi = trade_meta.get("hi", trade)

        explanation_en = (
            f"Recommended daily wage for {trade_meta['name']} in {city} ({city_tier}) "
            f"with {experience_years} years experience is ₹{recommended_daily:,.0f} "
            f"(Fair range: ₹{min_fair_wage:,.0f} - ₹{max_fair_wage:,.0f}/day)."
        )

        explanation_kn = (
            f"{city} ನಗರದಲ್ಲಿ ({city_tier}) {experience_years} ವರ್ಷಗಳ ಅನುಭವವಿರುವ "
            f"{trade_kn} ಕೆಲಸಕ್ಕೆ ನ್ಯಾಯಯುತ ದಿನಗೂಲಿ ₹{recommended_daily:,.0f} ಆಗಿದೆ "
            f"(ಕನಿಷ್ಠ ಸೂಕ್ತ ದರ: ₹{min_fair_wage:,.0f} ರಿಂದ ₹{max_fair_wage:,.0f}/ದಿನ)."
        )

        explanation_hi = (
            f"{city} ({city_tier}) में {experience_years} वर्ष के अनुभव वाले "
            f"{trade_hi} के लिए उचित दैनिक मजदूरी ₹{recommended_daily:,.0f} है "
            f"(स्वीकार्य सीमा: ₹{min_fair_wage:,.0f} से ₹{max_fair_wage:,.0f}/दिन)."
        )

        return {
            "trade": trade_meta["name"],
            "city": city,
            "city_tier": city_tier,
            "experience_years": experience_years,
            "recommended_daily_wage": float(recommended_daily),
            "recommended_hourly_wage": float(hourly_wage),
            "fair_wage_min": float(min_fair_wage),
            "fair_wage_max": float(max_fair_wage),
            "wage_bracket": wage_bracket,
            "factors": {
                "base_rate": base_rate,
                "tier_multiplier": tier_multiplier,
                "experience_multiplier": round(exp_multiplier, 2),
                "tool_premium": tool_premium,
                "urgency_multiplier": urgency_multiplier,
                "category": trade_meta["category"]
            },
            "regional_explanations": {
                "english": explanation_en,
                "kannada": explanation_kn,
                "hindi": explanation_hi
            }
        }
