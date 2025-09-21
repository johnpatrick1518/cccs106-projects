import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact
def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 420
    page.window.height = 650
    page.scroll = ft.ScrollMode.AUTO   
    page.padding = 20

    page.theme_mode = ft.ThemeMode.LIGHT

    def theme_change(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        toggle_label.value = (
            "Light Mode" if page.theme_mode == ft.ThemeMode.LIGHT else "Dark Mode"
        )
        page.update()

    db_conn = init_db()

    name_input = ft.TextField(label="Name", prefix_icon=ft.Icons.PERSON, width=350)
    phone_input = ft.TextField(label="Phone", prefix_icon=ft.Icons.PHONE, width=350)
    email_input = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL, width=350)

    inputs = (name_input, phone_input, email_input)

    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    add_button = ft.ElevatedButton(
        text="Add Contact",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    search_input = ft.TextField(
        label="Search",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, search_input.value or ""),
        width=380,
    )

    c = ft.Switch(on_change=theme_change)
    toggle_label = ft.Text("Light Mode", size=14, weight=ft.FontWeight.W_500)

    toggle_row = ft.Row(
        [toggle_label, ft.Container(content=c, scale=0.9)],
        alignment=ft.MainAxisAlignment.END,
        spacing=9
    )

    page.add(
        ft.Column(
            [
                ft.Row(
                        [
                            ft.Text("Contact Book", size=25, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Row([toggle_label, ft.Container(content=c, scale=0.9)], spacing=12)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                                name_input,
                                phone_input,
                                email_input,
                                add_button,
                            ],
                            spacing=10,
                        ),
                        padding=15,
                    )
                ),

                search_input,

                ft.Divider(thickness=1),
                ft.Text("Contacts", size=18, weight=ft.FontWeight.BOLD),

                contacts_list_view,
            ],
            spacing=10,
            expand=True,
        )
    )

    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)
