import tkinter as tk
from tkinter import messagebox
import requests

from city_info import show_city_info
from city_details import translate_text

API_KEY = "AIzaSyCRPLbjAcLZQ6yirVrUlUFfUGSPtTQRAUY"

TRANSLATE_API_KEY = "AIzaSyCRPLbjAcLZQ6yirVrUlUFfUGSPtTQRAUY"

window = tk.Tk()
window.title("여행 정보 프로그램")
window.geometry("900x600")
window.resizable(False, False)
window.configure(bg="lightyellow")

label = tk.Label(window, text="국가 이름을 입력하세요:", font=("Arial", 24), fg="darkblue", bg="lightyellow")
label.pack(pady=10)

entry = tk.Entry(window, font=("Arial", 20), width=30)
entry.pack()

def open_new_window():
    country_name = entry.get()

    try:
        translated_country_name = translate_text(country_name, "en")

        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": translated_country_name,
            "inputtype": "textquery",
            "fields": "name,types",
            "key": API_KEY
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data["candidates"]:
            raise ValueError("응답 데이터에 'candidates' 필드가 없습니다.")

        if "country" not in data["candidates"][0]["types"]:
            raise ValueError("잘못 입력했습니다.")

        params = {
            "input": f"{translated_country_name} cities",
            "inputtype": "textquery",
            "fields": "formatted_address,name,geometry,types,place_id",
            "rankby": "prominence",
            "key": API_KEY
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "candidates" not in data:
            raise ValueError("응답 데이터에 'candidates' 필드가 없습니다.")

        seen_place_ids = set()
        cities = [
            candidate
            for candidate in data["candidates"]
            if (
                any(type in candidate["types"] for type in ["locality", "political"])
                and candidate["name"] != translated_country_name
                and candidate["place_id"] not in seen_place_ids
                and not seen_place_ids.add(candidate["place_id"])
            )
        ]

        new_window = tk.Toplevel(window)
        new_window.title(f"{country_name} 주요 도시")
        new_window.geometry("900x600")
        new_window.resizable(False, False)
        new_window.configure(bg="lightyellow")

        def on_closing():
            for button in new_window.winfo_children():
                if isinstance(button, tk.Button):
                    button.config(state=tk.DISABLED)
            new_window.destroy()

        new_window.protocol("WM_DELETE_WINDOW", on_closing)

        if cities:
            for city in cities[:5]:
                button = tk.Button(
                    new_window,
                    text=city["name"],
                    font=("Arial", 14),
                    fg="blue",
                    bg="lightyellow",
                    command=lambda c=city: show_city_info(c, new_window)
                )
                button.pack(pady=5)
        else:
            tk.Label(new_window, text="주요 도시 정보를 찾을 수 없습니다.", font=("Arial", 16), fg="red", bg="lightyellow").pack(pady=20)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("오류", f"API 요청 오류: {e}")
    except ValueError as e:
        messagebox.showerror("오류", str(e))
    except Exception as e:
        messagebox.showerror("오류", f"예상치 못한 오류: {e}")

button = tk.Button(window, text="확인", command=open_new_window)
button.pack(pady=10)

window.bind('<Return>', lambda event: open_new_window())

window.mainloop()