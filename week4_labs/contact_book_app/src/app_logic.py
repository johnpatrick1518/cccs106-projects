import re
import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[\d\s\-\(\)]{11}$")

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return EMAIL_REGEX.match(email.strip()) is not None

def is_valid_phone(phone: str) -> bool:
    if not phone:
        return False
    return PHONE_REGEX.match(phone.strip()) is not None

def display_contacts(page, contacts_list_view, db_conn, search_term=""):
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)

    for contact in contacts:
        contact_id, name, phone, email = contact
        contacts_list_view.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(name, weight=ft.FontWeight.BOLD, size=16),
                                    ft.PopupMenuButton(
                                        icon=ft.Icons.MORE_VERT,
                                        items=[
                                            ft.PopupMenuItem(
                                                text="Edit",
                                                icon=ft.Icons.EDIT,
                                                on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view),
                                            ),
                                            ft.PopupMenuItem(),
                                            ft.PopupMenuItem(
                                                text="Delete",
                                                icon=ft.Icons.DELETE,
                                                on_click=lambda _, cid=contact_id: delete_contact(page, cid, db_conn, contacts_list_view),
                                            ),
                                        ],
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row(
                                    [
                                        ft.Icon(ft.Icons.PHONE, size=16),
                                        ft.Text(phone or "N/A"),
                                    ],
                                    spacing=5,
                                ),
                            ft.Row(
                                    [
                                        ft.Icon(ft.Icons.EMAIL, size=16),
                                        ft.Text(email or "N/A"),
                                    ],
                                    spacing=5,
                                ),
                        ],
                        spacing=5,
                    ),
                    padding=10,
                ),
            )
        )
    page.update()

def add_contact(page, inputs, contacts_list_view, db_conn):
    name_input, phone_input, email_input = inputs

    name = (name_input.value or "").strip()
    phone = (phone_input.value or "").strip()
    email = (email_input.value or "").strip()

    if not name:
        name_input.error_text = "Name cannot be empty"
        page.update()
        return
    else:
        name_input.error_text = None

    if not phone and not email:
        phone_input.error_text = "Provide phone or email"
        email_input.error_text = "Provide phone or email"
        page.update()
        return
    else:
        phone_input.error_text = None
        email_input.error_text = None

    if phone and not is_valid_phone(phone):
        phone_input.error_text = "Invalid phone format"
        page.update()
        return
    else:
        phone_input.error_text = None

    if email and not is_valid_email(email):
        email_input.error_text = "Invalid email address"
        page.update()
        return
    else:
        email_input.error_text = None

    add_contact_db(db_conn, name, phone, email)

    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view):
    def confirm_delete(e):
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn)
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Yes", on_click=confirm_delete),
        ],
    )
    page.open(dialog)

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        new_name = (edit_name.value or "").strip()
        new_phone = (edit_phone.value or "").strip()
        new_email = (edit_email.value or "").strip()

        if not new_name:
            edit_name.error_text = "Name cannot be empty"
            page.update()
            return
        else:
            edit_name.error_text = None

        if not new_phone and not new_email:
            edit_phone.error_text = "Provide phone or email"
            edit_email.error_text = "Provide phone or email"
            page.update()
            return
        else:
            edit_phone.error_text = None
            edit_email.error_text = None

        if new_phone and not is_valid_phone(new_phone):
            edit_phone.error_text = "Invalid phone format"
            page.update()
            return
        else:
            edit_phone.error_text = None

        if new_email and not is_valid_email(new_email):
            edit_email.error_text = "Invalid email address"
            page.update()
            return
        else:
            edit_email.error_text = None

        update_contact_db(db_conn, contact_id, new_name, new_phone, new_email)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )

    page.open(dialog)
