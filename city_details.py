import requests

#구글맵 API
GOOGLE_PLACES_API_KEY = "AIzaSyCRPLbjAcLZQ6yirVrUlUFfUGSPtTQRAUY"

#구글 번역기 API
TRANSLATE_API_KEY = "AIzaSyCRPLbjAcLZQ6yirVrUlUFfUGSPtTQRAUY"

#도시 정보 API
OPENCAGE_API_KEY = "4396d8e5a8034927b48bac3a75ed2ba3"

#환율 API
FIXER_IO_API_KEY = "de07865abbe0ff607a1666c4466d592b"


def translate_text(text, target_language):
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "q": text,
        "target": target_language,
        "key": TRANSLATE_API_KEY
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data["data"]["translations"][0]["translatedText"]

def get_city_details(city):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": city["place_id"],
        "fields": "name,formatted_address,geometry",
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data["result"]


def get_city_info_from_opencage(latitude, longitude):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={OPENCAGE_API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    city_info = {}
    if data["results"]:
        result = data["results"][0]
        city_info["area"] = result["annotations"].get("area", {}).get("value")
        city_info["population"] = result["annotations"].get("population", {}).get("value")
        city_info["timezone"] = result["annotations"].get("timezone", {}).get("name")
        city_info["currency"] = result["annotations"].get("currency", {}).get("iso_code")
    return city_info


def get_exchange_rate(base_currency, target_currency="KRW"):
    url = f"http://data.fixer.io/api/latest?access_key={FIXER_IO_API_KEY}&base={base_currency}&symbols={target_currency}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if data["success"]:
        rate = data["rates"][target_currency]
        return f"1 {base_currency} = {rate:.2f} {target_currency}"
    else:
        return "환율 정보를 가져올 수 없습니다."

