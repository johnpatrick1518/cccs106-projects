# main.py
import asyncio
import flet as ft
from weather_service import WeatherService, WeatherServiceError
from history_service import HistoryService
from watchlist_service import WatchlistService
from config import Config


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.create_task(coro)


def main(page: ft.Page):
    # ---------- PAGE SETUP ----------
    page.title = "Weather App"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 900
    page.window.height = 750
    page.window.resizable = True
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO


    weather_service = WeatherService()
    history_service = HistoryService()
    watchlist_service = WatchlistService()

    # ---------- ALERT SYSTEM ----------
    current_snackbar = None

    def show_alert(message: str, type_: str = "info"):
        nonlocal current_snackbar

        icons = {
            "error": ft.Icons.ERROR_OUTLINE,
            "warning": ft.Icons.WARNING_AMBER_ROUNDED,
            "success": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "info": ft.Icons.INFO_OUTLINE,
            "alert": ft.Icons.WB_SUNNY,
        }
        colors = {
            "error": ft.Colors.RED_600,
            "warning": ft.Colors.AMBER_700,
            "success": ft.Colors.GREEN_600,
            "info": ft.Colors.BLUE_600,
            "alert": ft.Colors.DEEP_ORANGE_600,
        }

        if current_snackbar:
            page.close(current_snackbar)

        snackbar = ft.SnackBar(
            bgcolor=colors.get(type_, ft.Colors.BLUE_600),
            content=ft.Row(
                [
                    ft.Icon(icons.get(type_, ft.Icons.INFO_OUTLINE), color=ft.Colors.WHITE),
                    ft.Text(message, color=ft.Colors.WHITE, size=15, weight=ft.FontWeight.W_600),
                ],
                spacing=10,
            ),
            duration=4000,
        )
        current_snackbar = snackbar
        page.open(snackbar)
        page.update()

    # ---------- TOGGLES ----------
    def toggle_theme():
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_icon.icon = ft.Icons.DARK_MODE
            show_alert("Dark mode enabled 🌙", "info")
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_icon.icon = ft.Icons.LIGHT_MODE
            show_alert("Light mode enabled ☀️", "info")
        page.update()
        update_card_styles()

    def toggle_units():
        if Config.UNITS == "metric":
            Config.UNITS = "imperial" # type: ignore
            unit_icon.content = ft.Text("°F", size=18, weight=ft.FontWeight.BOLD)
            show_alert("Switched to Fahrenheit (°F)", "info")
        else:
            Config.UNITS = "metric"
            unit_icon.content = ft.Text("°C", size=18, weight=ft.FontWeight.BOLD)
            show_alert("Switched to Celsius (°C)", "info")
        page.update()

    # ---------- HEADER ----------
    title = ft.Text("🌤️ Weather App", size=32, weight=ft.FontWeight.BOLD)

    theme_icon = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Toggle theme",
        icon_size=28,
        on_click=lambda e: toggle_theme(),
    )

    unit_icon = ft.IconButton(
        content=ft.Text("°C", size=18, weight=ft.FontWeight.BOLD),
        tooltip="Switch units",
        on_click=lambda e: toggle_units(),
    )

    header = ft.Row(
        [title, ft.Row([unit_icon, theme_icon], spacing=10)],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        width=850,
    )

    # ---------- SEARCH + WATCHLIST ----------
    city_input = ft.TextField(
        label="Enter city name",
        width=600,
        height=60,
        on_focus=lambda e: show_recent_history(),
        on_submit=lambda e: fetch_weather(city_input.value),
        autofocus=True,
        hint_text="e.g., London, Tokyo, New York",
        border_color=ft.Colors.BLUE_400,
        prefix_icon=ft.Icons.LOCATION_CITY,
    )

    search_button = ft.ElevatedButton("🔍 Search", on_click=lambda e: fetch_weather(city_input.value))
    add_watchlist_btn = ft.IconButton(icon=ft.Icons.BOOKMARK_ADD_OUTLINED, tooltip="Add to watchlist",
                                      on_click=lambda e: add_to_watchlist())
    view_watchlist_btn = ft.IconButton(icon=ft.Icons.VIEW_LIST, tooltip="Compare watchlist cities",
                                       on_click=lambda e: run_async(view_watchlist()))

    search_row = ft.Row(
        [city_input, search_button, add_watchlist_btn, view_watchlist_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    # ---------- OUTPUT AREAS ----------
    weather_card = ft.Container(
        width=850,
        border_radius=16,
        padding=20,
        content=ft.Column([], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )
    forecast_section = ft.Column(spacing=10)
    watchlist_section = ft.Column(spacing=10)

    def update_card_styles():
        """Apply theme-aware background colors."""
        bg_color = ft.Colors.BLUE_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_900
        weather_card.bgcolor = bg_color
        for section in [forecast_section, watchlist_section]:
            for ctrl in section.controls:
                if isinstance(ctrl, ft.Container):
                    ctrl.bgcolor = bg_color
        page.update()

    # ---------- LAYOUT ----------
    layout = ft.Column(
        [
            header,
            ft.Divider(),
            search_row,
            weather_card,
            ft.Divider(),
            forecast_section,
            watchlist_section,
        ],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    page.add(layout)

    # ---------- EVENT HANDLERS ----------
    def show_recent_history():
        recent = history_service.get_history()
        if not recent:
            return
        city_input.suffix = ft.PopupMenuButton(
            items=[ft.PopupMenuItem(text=c, on_click=lambda e, city=c: fill_city(city)) for c in recent]
        )
        page.update()

    def fill_city(city):
        city_input.value = city
        page.update()
        fetch_weather(city)

    def add_to_watchlist():
        city_name = (city_input.value or "").strip()
        if not city_name:
            show_alert("Enter a city before adding to watchlist.", "warning")
            return
        watchlist_service.add_city(city_name)
        show_alert(f"{city_name.title()} added to watchlist ✅", "success")

    async def view_watchlist():
        cities = watchlist_service.get_watchlist()
        if not cities:
            show_alert("Your watchlist is empty.", "info")
            return

        watchlist_section.controls = [ft.Text("🌍 City Comparison", size=20, weight=ft.FontWeight.BOLD)]
        page.update()

        async def fetch_city(city):
            try:
                data = await weather_service.get_weather(city)
                name = data.get("name", city)
                main = data.get("main", {})
                weather = data.get("weather", [{}])[0]
                temp = main.get("temp", "N/A")
                cond = weather.get("description", "N/A").capitalize()
                icon = weather.get("icon", "01d")
                icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
                color = ft.Colors.BLUE_100 if "clear" in cond.lower() else (
                    ft.Colors.GREY_300 if "cloud" in cond.lower() else ft.Colors.BLUE_200)

                return ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                            ft.Image(src=icon_url, width=60, height=60),
                            ft.Text(f"{temp}°{('C' if Config.UNITS == 'metric' else 'F')}", size=18),
                            ft.Text(cond, size=14),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Remove from watchlist",
                                on_click=lambda e, c=name: remove_from_watchlist(c),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    width=160,
                    height=200,
                    bgcolor=color if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_800,
                    border_radius=12,
                    padding=10,
                )
            except Exception:
                return ft.Container(content=ft.Text(f"{city}: ❌ Error"), width=160)

        results = await asyncio.gather(*(fetch_city(c) for c in cities))
        watchlist_section.controls.extend([ft.Row(results, wrap=True, spacing=10)])
        page.update()

    def remove_from_watchlist(city):
        watchlist_service.remove_city(city)
        show_alert(f"{city} removed from watchlist 🗑️", "info")
        run_async(view_watchlist())

    async def fetch_and_display(city: str):
        try:
            data = await weather_service.get_weather(city)
        except WeatherServiceError as exc:
            show_alert(str(exc), "error")
            return
        except Exception as exc:
            show_alert(f"Unexpected error: {exc}", "error")
            return

        name = data.get("name", city)
        sys = data.get("sys", {})
        country = sys.get("country", "")
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})

        temp = main.get("temp", "N/A")
        humidity = main.get("humidity", "N/A")
        condition = weather.get("description", "N/A").capitalize()
        wind_speed = wind.get("speed", "N/A")
        pressure = main.get("pressure", "N/A")
        clouds = data.get("clouds", {}).get("all", "N/A")
        icon_code = weather.get("icon", "01d")

        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        weather_icon = ft.Image(src=icon_url, width=100, height=100)

        # --- Weather alerts ---
        if isinstance(temp, (int, float)):
            if temp > 35:
                show_alert(f"🔥 Hot weather alert! {temp}°C", "alert")
            elif temp < 5:
                show_alert(f"❄️ Cold weather alert! {temp}°C", "alert")
            elif "storm" in condition.lower():
                show_alert("⛈️ Storm alert!", "alert")

        # --- Dynamic background gradient ---
        bg_gradient = ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=(
                [ft.Colors.LIGHT_BLUE_200, ft.Colors.BLUE_100]
                if "clear" in condition.lower()
                else [ft.Colors.GREY_400, ft.Colors.BLUE_GREY_200]
                if "cloud" in condition.lower()
                else [ft.Colors.INDIGO_200, ft.Colors.BLUE_300]
            ),
        )

        weather_card.bgcolor = None
        weather_card.gradient = bg_gradient

        weather_card.content.controls = [ # type: ignore
            ft.Text(f"📍 {name}, {country}", size=18, weight=ft.FontWeight.BOLD),
            weather_icon,
            ft.Text(condition, size=16, italic=True),
            ft.Text(
                f"{temp}°{('C' if Config.UNITS == 'metric' else 'F')}",
                size=40,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_900,
            ),
            ft.Row(
                [
                    ft.Text(f"Humidity: {humidity}%", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Wind: {wind_speed} {'m/s' if Config.UNITS == 'metric' else 'mph'}", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Pressure: {pressure} hPa", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Clouds: {clouds}%", size=14, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                wrap=True,
            ),
        ]
        page.update()

        history_service.add_city(name)
        run_async(fetch_and_display_forecast(city))

    async def fetch_and_display_forecast(city: str):
        try:
            data = await weather_service.get_forecast(city)
        except Exception:
            show_alert("Could not load forecast.", "warning")
            return

        forecast_list = data.get("list", [])
        if not forecast_list:
            return

        forecast_section.controls = [ft.Text("📅 5-Day Forecast", size=20, weight=ft.FontWeight.BOLD)]
        displayed_dates = set()

        for item in forecast_list:
            dt_txt = item.get("dt_txt", "")
            date = dt_txt.split(" ")[0]
            if date in displayed_dates:
                continue
            displayed_dates.add(date)

            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            temp = main.get("temp", "N/A")
            cond = weather.get("description", "N/A").capitalize()
            icon = weather.get("icon", "01d")
            icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"

            color = (
                ft.Colors.LIGHT_BLUE_100 if "clear" in cond.lower()
                else ft.Colors.GREY_300 if "cloud" in cond.lower()
                else ft.Colors.INDIGO_100
            )

            card = ft.Container(
                width=130,
                bgcolor=color if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_800,
                border_radius=12,
                padding=10,
                content=ft.Column(
                    [
                        ft.Text(date, size=14, weight=ft.FontWeight.W_600),
                        ft.Image(src=icon_url, width=60, height=60),
                        ft.Text(f"{temp}°", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(cond, size=12, italic=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            forecast_section.controls.append(card)

        page.update()

    def fetch_weather(city=None):
        city_name = (city or city_input.value or "").strip()
        if not city_name:
            show_alert("Please enter a city name.", "warning")
            return
        weather_card.content.controls = [ft.Text(f"Fetching weather for {city_name}...", color=ft.Colors.AMBER)] # type: ignore
        page.update()
        run_async(fetch_and_display(city_name))

    page.update()


if __name__ == "__main__":
    ft.app(target=main)
