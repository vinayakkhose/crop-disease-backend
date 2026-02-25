"""
Weather Service — uses Open-Meteo (free, no API key required) for real weather
data and a research-backed disease risk model that considers humidity, temperature,
precipitation, dew point spread, and cloud cover.
"""

import httpx
from typing import Dict, Optional
import os

# ---------------------------------------------------------------------------
# Geocoding helper (Open-Meteo geocoding, also free)
# ---------------------------------------------------------------------------
GEO_URL   = "https://geocoding-api.open-meteo.com/v1/search"
METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Optional: still honour a user-supplied OpenWeatherMap key as a fallback
OWM_KEY  = os.getenv("WEATHER_API_KEY", "")
OWM_URL  = "https://api.openweathermap.org/data/2.5/weather"


class WeatherService:
    """Fetches real weather data and scores crop-disease risk."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def get_weather_data(self, region: str) -> Optional[Dict]:
        """
        Return weather + disease-risk dict for a region name.
        Tries in order:
          1. Open-Meteo (free, no key)  ← primary
          2. OpenWeatherMap (if key set in env)
          3. Realistic fallback (clearly labelled as estimated)
        """
        data = await self._try_open_meteo(region)
        if data:
            return data

        if OWM_KEY:
            data = await self._try_owm(region)
            if data:
                return data

        # Last resort: deterministic-but-realistic fallback
        return self._region_fallback(region)

    # ------------------------------------------------------------------
    # Source 1: Open-Meteo (free, no API key needed)
    # ------------------------------------------------------------------
    async def _try_open_meteo(self, region: str) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                # Step 1 – geocode the region name
                geo_resp = await client.get(GEO_URL, params={"name": region, "count": 1, "language": "en", "format": "json"})
                geo_resp.raise_for_status()
                geo = geo_resp.json()
                results = geo.get("results")
                if not results:
                    return None

                lat = results[0]["latitude"]
                lon = results[0]["longitude"]
                city_name = results[0].get("name", region)
                country   = results[0].get("country", "")

                # Step 2 – fetch current weather
                params = {
                    "latitude":  lat,
                    "longitude": lon,
                    "current":   [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "precipitation",
                        "cloud_cover",
                        "dew_point_2m",
                        "wind_speed_10m",
                    ],
                    "timezone": "auto",
                }
                wx_resp = await client.get(METEO_URL, params=params)
                wx_resp.raise_for_status()
                wx = wx_resp.json().get("current", {})

                temperature   = float(wx.get("temperature_2m",        20))
                humidity      = float(wx.get("relative_humidity_2m",   50))
                precipitation = float(wx.get("precipitation",           0))
                cloud_cover   = float(wx.get("cloud_cover",            50))
                dew_point     = float(wx.get("dew_point_2m",           10))
                wind_speed    = float(wx.get("wind_speed_10m",          5))

                risk_level, risk_factors = self._calculate_disease_risk(
                    humidity, temperature, precipitation, cloud_cover, dew_point, wind_speed
                )

                return {
                    "source":        "Open-Meteo (live)",
                    "location":      f"{city_name}, {country}".strip(", "),
                    "humidity":      round(humidity, 1),
                    "temperature":   round(temperature, 1),
                    "precipitation": round(precipitation, 1),
                    "cloud_cover":   round(cloud_cover, 1),
                    "dew_point":     round(dew_point, 1),
                    "wind_speed":    round(wind_speed, 1),
                    "risk_level":    risk_level,
                    "risk_factors":  risk_factors,
                }
        except Exception as exc:
            print(f"[WeatherService] Open-Meteo error for '{region}': {exc}")
            return None

    # ------------------------------------------------------------------
    # Source 2: OpenWeatherMap (needs WEATHER_API_KEY env var)
    # ------------------------------------------------------------------
    async def _try_owm(self, region: str) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient(timeout=6) as client:
                resp = await client.get(OWM_URL, params={
                    "q": region, "appid": OWM_KEY, "units": "metric"
                })
                resp.raise_for_status()
                data = resp.json()

                temperature   = float(data["main"]["temp"])
                humidity      = float(data["main"]["humidity"])
                precipitation = float(data.get("rain", {}).get("1h", 0))
                cloud_cover   = float(data.get("clouds", {}).get("all", 50))
                # OWM doesn't return dew point directly — estimate it
                dew_point = temperature - ((100 - humidity) / 5)
                wind_speed = float(data.get("wind", {}).get("speed", 5))

                risk_level, risk_factors = self._calculate_disease_risk(
                    humidity, temperature, precipitation, cloud_cover, dew_point, wind_speed
                )

                return {
                    "source":        "OpenWeatherMap (live)",
                    "location":      data.get("name", region),
                    "humidity":      round(humidity, 1),
                    "temperature":   round(temperature, 1),
                    "precipitation": round(precipitation, 1),
                    "cloud_cover":   round(cloud_cover, 1),
                    "dew_point":     round(dew_point, 1),
                    "wind_speed":    round(wind_speed, 1),
                    "risk_level":    risk_level,
                    "risk_factors":  risk_factors,
                }
        except Exception as exc:
            print(f"[WeatherService] OWM error for '{region}': {exc}")
            return None

    # ------------------------------------------------------------------
    # Source 3: Deterministic fallback (no network)
    # ------------------------------------------------------------------
    def _region_fallback(self, region: str) -> Dict:
        h = abs(hash(region.strip().lower())) % 10000
        temperature   = round(15 + (h % 25), 1)
        humidity      = round(40 + (h % 50), 1)
        precipitation = round((h % 30) / 10.0, 1)
        cloud_cover   = round(20 + (h % 60), 1)
        dew_point     = round(temperature - ((100 - humidity) / 5), 1)
        wind_speed    = round(2 + (h % 15), 1)

        risk_level, risk_factors = self._calculate_disease_risk(
            humidity, temperature, precipitation, cloud_cover, dew_point, wind_speed
        )
        return {
            "source":        "Estimated (no network / unknown location)",
            "location":      region,
            "humidity":      humidity,
            "temperature":   temperature,
            "precipitation": precipitation,
            "cloud_cover":   cloud_cover,
            "dew_point":     dew_point,
            "wind_speed":    wind_speed,
            "risk_level":    risk_level,
            "risk_factors":  risk_factors,
        }

    # ------------------------------------------------------------------
    # Research-backed disease risk model
    # ------------------------------------------------------------------
    def _calculate_disease_risk(
        self,
        humidity:      float,
        temperature:   float,
        precipitation: float,
        cloud_cover:   float = 50,
        dew_point:     float = 10,
        wind_speed:    float = 5,
    ):
        """
        Score: 0-10 across 5 agronomic risk factors.

        Reference ranges from plant pathology literature:
        - Fungal diseases (early/late blight, gray mold): RH > 80%, T 15-25°C
        - Bacterial diseases: RH > 85%, T 25-35°C
        - Downy mildew: RH > 90%, T 10-20°C
        """
        score = 0
        factors = []

        # 1. Relative Humidity (weight: 3)
        if humidity > 90:
            score += 3
            factors.append("Very high humidity (>90%) — critical fungal/bacterial risk")
        elif humidity > 80:
            score += 2
            factors.append("High humidity (>80%) — favourable for fungal spread")
        elif humidity > 65:
            score += 1
            factors.append("Moderate humidity — some disease pressure possible")

        # 2. Temperature (weight: 3)
        if 15 <= temperature <= 30:
            if 20 <= temperature <= 28:
                score += 3
                factors.append(f"Temperature {temperature}°C — optimal range for most pathogens")
            else:
                score += 2
                factors.append(f"Temperature {temperature}°C — within disease-conducive range")
        elif 10 <= temperature < 15:
            score += 1
            factors.append(f"Temperature {temperature}°C — cool; downy mildew risk elevated")

        # 3. Precipitation (weight: 2)
        if precipitation > 5:
            score += 2
            factors.append(f"Heavy rainfall ({precipitation}mm) — splash dispersal likely")
        elif precipitation > 0:
            score += 1
            factors.append(f"Rainfall present ({precipitation}mm) — leaf wetness increased")

        # 4. Cloud cover / low light (weight: 1) — slows crop drying
        if cloud_cover > 75:
            score += 1
            factors.append("Heavy cloud cover — leaves stay wet longer")

        # 5. Dew point spread (weight: 1)
        # When dew point is close to air temp (<3°C spread), dew forms on leaves
        spread = temperature - dew_point
        if spread < 3:
            score += 1
            factors.append("Dew point near air temp — overnight dew/condensation likely")

        # Bonus: calm wind keeps spores localised
        if wind_speed < 3 and score >= 3:
            score += 1
            factors.append("Low wind speed — airborne spores not dispersed, local spread intensified")

        # Map score to risk level
        if score >= 7:
            risk_level = "high"
        elif score >= 4:
            risk_level = "moderate"
        else:
            risk_level = "low"

        if not factors:
            factors.append("Conditions currently unfavourable for most crop diseases")

        return risk_level, factors


# Global singleton
weather_service = WeatherService()
