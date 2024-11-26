import tkinter as tk
from tkinter import messagebox
import requests
import webbrowser
import pytz
from datetime import datetime, timedelta

from city_details import get_exchange_rate, get_city_details, get_city_info_from_opencage, translate_text

#구글맵 API
GOOGLE_PLACES_API_KEY = "AIzaSyCRPLbjAcLZQ6yirVrUlUFfUGSPtTQRAUY"

def show_city_info(city, window):

    try:
        city_details = get_city_details(city)

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{city['geometry']['location']['lat']},{city['geometry']['location']['lng']}",
            "radius": 5000,
            "type": "tourist_attraction",
            "key": GOOGLE_PLACES_API_KEY
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "results" not in data:
            raise ValueError("응답 데이터에 'results' 필드가 없습니다.")

        attractions = data["results"]

        info_window = tk.Toplevel(window)
        info_window.title(f"{city['name']} 관광 명소")
        info_window.geometry("900x600")
        info_window.configure(bg="lightyellow")

        city_info_listbox = tk.Listbox(info_window, font=("Arial", 14), width=65, height=10, bg="lightyellow")
        city_info_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        city_info_listbox.insert("end", f"도시 이름: {city_details['name']}")
        city_info_listbox.insert("end", f"주소: {city_details['formatted_address']}")

        latitude = city_details["geometry"]["location"]["lat"]
        longitude = city_details["geometry"]["location"]["lng"]
        opencage_city_info = get_city_info_from_opencage(latitude, longitude)

        if opencage_city_info["area"]:
            translated_area = translate_text(str(opencage_city_info["area"]), "ko")
            city_info_listbox.insert("end", f"면적: {translated_area} km²")
        if opencage_city_info["population"]:
            translated_population = translate_text(str(opencage_city_info["population"]), "ko")
            city_info_listbox.insert("end", f"인구: {translated_population}")

        if opencage_city_info["timezone"]:
            timezone_name = opencage_city_info["timezone"]

            try:
                timezone = pytz.timezone(timezone_name)
                timezone_datetime = timezone.localize(datetime.now())
                korea_timezone = pytz.timezone('Asia/Seoul')
                korea_datetime = korea_timezone.localize(datetime.now())
                time_difference = timezone_datetime - korea_datetime
                hours, remainder = divmod(int(time_difference.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                time_diff_str = f"{hours}시간 {minutes}분"

                translated_timezone = translate_text(timezone_name, "ko")
                city_info_listbox.insert("end", f"시간대: {translated_timezone} (KST와 {time_diff_str} 차이)")

            except pytz.exceptions.UnknownTimeZoneError:
                print(f"알 수 없는 시간대: {timezone_name}")
                city_info_listbox.insert("end", f"시간대: {timezone_name}")

        if opencage_city_info["currency"]:
            exchange_rate = get_exchange_rate(opencage_city_info["currency"])
            city_info_listbox.insert("end", f"화폐: {opencage_city_info['currency']}, {exchange_rate}")

        search_query = city['name']
        wikipedia_url = f"https://ko.wikipedia.org/wiki/{search_query}"
        hyperlink_text = f"도시에 대한 간략한 설명: {city['name']} Wikipedia"
        city_info_listbox.insert("end", hyperlink_text)

        listbox = tk.Listbox(info_window, font=("Arial", 14), width=65, height=10, bg="lightyellow")
        listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(info_window, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        def open_hyperlink(event):
            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                item = event.widget.get(index)
                if item == hyperlink_text:
                    webbrowser.open_new(wikipedia_url)

        city_info_listbox.bind("<Double-Button-1>", open_hyperlink)

        if attractions:
            for attraction in attractions:
                translated_name = translate_text(attraction['name'], "ko") 
                listbox.insert("end", f"{translated_name}")

                if "vicinity" in attraction:
                    translated_address = translate_text(attraction['vicinity'], "ko") 
                    listbox.insert("end", f"  주소: {translated_address}")
                    listbox.insert("end", "")
        else:
            listbox.insert("end", "관광 명소 정보를 찾을 수 없습니다.")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("오류", f"API 요청 오류: {e}")
        print(f"API 요청 오류: {e}")
    except ValueError as e:
        messagebox.showerror("오류", f"응답 데이터 오류: {e}")
        print(f"응답 데이터 오류: {e}")
    except Exception as e:
        messagebox.showerror("오류", f"예상치 못한 오류: {e}")
        print(f"예상치 못한 오류: {e}")