"""
Backwards-compatibility bridge.
Redirects to dedicated app.services.ivr_service.
"""
from app.services.ivr_service import IVRService, TelecomService, TRADE_OPTIONS, CITY_OPTIONS

__all__ = ["IVRService", "TelecomService", "TRADE_OPTIONS", "CITY_OPTIONS"]
