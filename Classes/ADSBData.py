from typing import Optional, List

class ADSBData:
    def __init__(
        self,
        alert: Optional[int] = None,
        alt_baro: Optional[int] = None,
        alt_geom: Optional[int] = None,
        baro_rate: Optional[int] = None,
        category: Optional[str] = None,
        dbFlags: Optional[int] = None,
        emergency: Optional[str] = None,
        flight: Optional[str] = None,
        gs: Optional[float] = None,
        gva: Optional[int] = None,
        hex: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        messages: Optional[int] = None,
        mlat: Optional[List[str]] = None,
        nac_p: Optional[int] = None,
        nac_v: Optional[int] = None,
        nav_altitude_mcp: Optional[int] = None,
        nav_heading: Optional[float] = None,
        nav_qnh: Optional[float] = None,
        nic: Optional[int] = None,
        nic_baro: Optional[int] = None,
        r: Optional[str] = None,
        rc: Optional[int] = None,
        rssi: Optional[float] = None,
        sda: Optional[int] = None,
        seen: Optional[float] = None,
        seen_pos: Optional[float] = None,
        sil: Optional[int] = None,
        sil_type: Optional[str] = None,
        spi: Optional[int] = None,
        squawk: Optional[str] = None,
        t: Optional[str] = None,
        tisb: Optional[List[str]] = None,
        track: Optional[float] = None,
        type: Optional[str] = None,
        version: Optional[int] = None
    ):
        self.alert = alert
        self.alt_baro = alt_baro
        self.alt_geom = alt_geom
        self.baro_rate = baro_rate
        self.category = category
        self.dbFlags = dbFlags
        self.emergency = emergency
        self.flight = flight
        self.gs = gs
        self.gva = gva
        self.hex = hex
        self.lat = lat
        self.lon = lon
        self.messages = messages
        self.mlat = mlat or []
        self.nac_p = nac_p
        self.nac_v = nac_v
        self.nav_altitude_mcp = nav_altitude_mcp
        self.nav_heading = nav_heading
        self.nav_qnh = nav_qnh
        self.nic = nic
        self.nic_baro = nic_baro
        self.r = r
        self.rc = rc
        self.rssi = rssi
        self.sda = sda
        self.seen = seen
        self.seen_pos = seen_pos
        self.sil = sil
        self.sil_type = sil_type
        self.spi = spi
        self.squawk = squawk
        self.t = t
        self.tisb = tisb or []
        self.track = track
        self.type = type
        self.version = version

    def to_dict(self):
        return self.__dict__