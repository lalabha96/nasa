import requests
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nasa_climate_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetches daily NASA POWER meteorological and solar records for given coordinates."""
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    raw = response.json()["properties"]["parameter"]
    
    df = pd.DataFrame(raw)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df = df.replace(-999.0, pd.NA).dropna()
    df = df.astype(float)
    df.index.name = "Date"
    
    # Rename columns for cleaner downstream usage
    df = df.rename(columns={
        "T2M": "Temp_Avg",
        "T2M_MAX": "Temp_Max",
        "T2M_MIN": "Temp_Min",
        "PRECTOTCORR": "Rainfall_mm",
        "RH2M": "Humidity_pct",
        "ALLSKY_SFC_SW_DWN": "Solar_kWh_m2"
    })
    return df