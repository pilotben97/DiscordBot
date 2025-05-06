from typing import Optional, List
from datetime import datetime

class Aircraft:
    def __init__(
        self,
        hexCode: str,
        icao: Optional[str] = None,
        callsign: Optional[str] = None,
        callsignAbbr: Optional[str] = None,
        tailNumber: Optional[str] = None,
        operator: Optional[str] = None,
        lastAirport: Optional[str] = None,
        lastDistance: Optional[str] = None,
        lastLat: Optional[str] = None,
        lastLon: Optional[str] = None,
        base: Optional[str] = None,
        companyCode: Optional[int] = None,
        lastSeenDate: Optional[datetime] = None,
        source: Optional[str] = None,
        notes: Optional[str] = None,
        lastAirports: Optional[List[str]] = None
    ):
        self.hexCode = hexCode.upper()
        self.icao = icao
        self.callsign = callsign
        self.callsignAbbr = callsignAbbr
        self.tailNumber = tailNumber
        self.operator = operator
        self.lastAirport = lastAirport
        self.lastDistance = lastDistance
        self.lastLat = lastLat
        self.lastLon = lastLon
        self.base = base
        self.companyCode = companyCode
        self.lastSeenDate = lastSeenDate
        self.source = source
        self.notes = notes
        self.lastAirports = (lastAirports or [])[:5]  # keep only first 5 if provided

    def __repr__(self):
        return f"Aircraft({self.__dict__})"

    def to_dict(self) -> dict:
        return {
            "hexCode": self.hexCode,
            "icao": self.icao,
            "callsign": self.callsign,
            "callsignAbbr": self.callsignAbbr,
            "tailNumber": self.tailNumber,
            "operator": self.operator,
            "lastAirport": self.lastAirport,
            "lastDistance": self.lastDistance,
            "lastLat": self.lastLat,
            "lastLon": self.lastLon,
            "base": self.base,
            "companyCode": self.companyCode,
            "lastSeenDate": self.lastSeenDate.isoformat() if self.lastSeenDate else None,
            "source": self.source,
            "notes": self.notes,
            "lastAirports": ",".join(self.lastAirports) if self.lastAirports else "",
        }