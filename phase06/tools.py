import os
import httpx
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.
    
    Args:
        city: The name of the city (e.g., "London", "Tokyo")
    
    Returns:
        Current weather conditions.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key:
        return "Error: WEATHER_API_KEY not set in .env"
    
    try:
        response = httpx.get(
            "http://api.weatherapi.com/v1/current.json",
            params={"key": api_key, "q": city},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        
        location = data["location"]["name"]
        country = data["location"]["country"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]
        
        return f"""Weather for {location}, {country}:
🌡️ Temperature: {temp_c}°C
☁️ Condition: {condition}
💧 Humidity: {humidity}%"""
        
    except httpx.HTTPStatusError:
        return f"Could not find weather for '{city}'"
    except Exception as e:
        return f"Error: {e}"


TOOLS = [get_weather]