import flet as ft
import mysql.connector
from db_connection import connect_db


def main(page: ft.Page):
    page.title = "User Login"
    page.window.center()
    page.window.frameless = True
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.always_on_top = True
    page.window.resizable = False
    page.window.title_bar_buttons_hidden = True
    page.theme_mode = ft.ThemeMode.LIGHT

    login_title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.BLACK,
    )

    username = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        icon=ft.Icons.PERSON,
        fill_color=ft.Colors.LIGHT_BLUE_ACCENT
    )

    password = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,
        can_reveal_password=True,
        autofocus=True,
        icon=ft.Icons.PASSWORD,
        fill_color=ft.Colors.LIGHT_BLUE_ACCENT
    )

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    def show_dialog(title, message, icon, color):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column(
                [
                    ft.Icon(icon, color=color, size=40),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Text(message, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(dialog))],
        )
        page.overlay.append(dialog)  
        dialog.open = True
        page.update()

    def login_click(e):
        uname = (username.value or "").strip()
        pword = (password.value or "").strip()

        if not uname or not pword:
            show_dialog("Input Error", "Please enter username and password", ft.Icons.INFO, ft.Colors.BLUE)
            return

        try:
            conn = connect_db()
            if conn is None:
                show_dialog("Database Error", "Could not connect to the database.", ft.Icons.ERROR, ft.Colors.RED)
                return
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (uname, pword),
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                show_dialog("Login Successful", f"Welcome, {uname}!", ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN)
            else:
                show_dialog("Login Failed", "Invalid username or password", ft.Icons.ERROR, ft.Colors.RED)

        except mysql.connector.Error as err:
            print(f"❌ Database Error: {err}")
            show_dialog("Database Error", "An error occurred while connecting to the database", ft.Icons.ERROR, ft.Colors.RED)

    login_button = ft.ElevatedButton(
        "Login", on_click=login_click, width=100, icon=ft.Icons.LOGIN
    )

    
    page.add(
        login_title,
        ft.Container(
            content=ft.Column([username, password], spacing=20),
            alignment=ft.alignment.center,
        ),
        ft.Container(
            content=login_button,
            alignment=ft.alignment.top_right,
            margin=ft.Margin(0, 20, 40, 0),
        ),
    )

ft.app(target=main)
if __name__ == "__main__":
    ft.app(target=main)