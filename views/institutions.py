import flet as ft
from flet_route import Params, Basket
import mysql.connector
import re
from .conections import create_connection

FG = '#B7C1F3'
BG = '#8C81BF'

def Institutions(page: ft.Page, params: Params, basket: Basket):

    # Assume administrator ID is passed in params
    admin_id = params.get("my_id")

    page.title = 'Institutions Management'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 900
    page.window_height = 500

    def fetch_institutions(admin_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM institution WHERE id_administrator = %s", (admin_id,))
        institutions = cursor.fetchall()
        conn.close()
        return institutions

    def add_institution(name, address, telephone, email, admin_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO institution (name, address, telephone, email, id_administrator) VALUES (%s, %s, %s, %s, %s)", 
                       (name, address, telephone, email, admin_id))
        conn.commit()
        conn.close()
        refresh_institutions_table()
        show_confirmation_snackbar("Institution added successfully.")

    def edit_institution(inst_id, name, address, telephone, email):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE institution SET name = %s, address = %s, telephone = %s, email = %s WHERE id_institution = %s", 
                       (name, address, telephone, email, inst_id))
        conn.commit()
        conn.close()
        refresh_institutions_table()        
        show_confirmation_snackbar("Institution updated successfully.")

    def delete_institution(inst_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM institution WHERE id_institution = %s", (inst_id,))
        conn.commit()
        conn.close()
        refresh_institutions_table()
        show_confirmation_snackbar("Institution deleted successfully.")

    def refresh_institutions_table():
        institutions = fetch_institutions(admin_id)
        institutions_table.rows.clear()
        institutions_table.rows.extend([
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(inst[0]), color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(inst[1], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(inst[2], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(inst[3], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(inst[4], color=ft.colors.BLACK)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, inst=inst: open_edit_institution_dialog(inst)),
                                ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, inst=inst: delete_institution(inst[0]))
                            ]
                        )
                    )
                ]
            )
            for inst in institutions
        ])
        page.update()

    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def open_add_institution_dialog(e):
        dialog.open = True
        dialog_title.value = "Add Institution"
        name_input.value = ""
        address_input.value = ""
        telephone_input.value = ""
        email_input.value = ""
        save_button.on_click = save_new_institution
        save_button.disabled = True
        cancel_button.on_click = cancel
        page.update()

    def save_new_institution(e):
        add_institution(name_input.value, address_input.value, telephone_input.value, email_input.value, admin_id)
        dialog.open = False
        page.update()

    def cancel(e):
        dialog.open = False
        page.update()

    def open_edit_institution_dialog(inst):
        dialog.open = True
        dialog_title.value = "Edit Institution"
        name_input.value = inst[1]
        address_input.value = inst[2]
        telephone_input.value = inst[3]
        email_input.value = inst[4]
        save_button.on_click = lambda e: save_edited_institution(inst[0])
        save_button.disabled = False
        cancel_button.on_click = cancel
        page.update()

    def save_edited_institution(inst_id):
        edit_institution(inst_id, name_input.value, address_input.value, telephone_input.value, email_input.value)
        dialog.open = False
        page.update()

    def validate_fields(e):
        name_valid = bool(name_input.value.strip())
        address_valid = bool(address_input.value.strip())
        telephone_valid = bool(telephone_input.value.strip())
        email_valid = bool(re.match(r"[^@]+@[^@]+\.[^@]+", email_input.value.strip()))

        if not name_valid:
            name_input.error_text = "Name cannot be empty."
        else:
            name_input.error_text = None
        
        if not address_valid:
            address_input.error_text = "Address cannot be empty."
        else:
            address_input.error_text = None
        
        if not telephone_valid:
            telephone_input.error_text = "Telephone cannot be empty."
        else:
            telephone_input.error_text = None
        
        if not email_valid:
            email_input.error_text = "Invalid email format."
        else:
            email_input.error_text = None

        save_button.disabled = not (name_valid and address_valid and telephone_valid and email_valid)
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(),
        content=ft.Column(
            [
                ft.TextField(label="Name", on_change=validate_fields),
                ft.TextField(label="Address", on_change=validate_fields),
                ft.TextField(label="Telephone", on_change=validate_fields),
                ft.TextField(label="Email", on_change=validate_fields)
            ],
            tight=True,
            spacing=10
        ),
        actions=[
            ft.ElevatedButton(text="Save", on_click=None),
            ft.OutlinedButton(text="Cancel", on_click=None)
        ]
    )
    dialog_title = dialog.title
    name_input = dialog.content.controls[0]
    address_input = dialog.content.controls[1]
    telephone_input = dialog.content.controls[2]
    email_input = dialog.content.controls[3]
    save_button = dialog.actions[0]
    cancel_button = dialog.actions[1]

    institutions_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Name", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Address", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Telephone", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Email", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Actions", color=ft.colors.BLACK))
        ],
        rows=[],
        column_spacing=15,
        data_row_color=ft.colors.WHITE,
        heading_row_color=BG
    )

    add_institution_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_institution_dialog)

    refresh_institutions_table()

    return ft.View(
        "/institutions/:my_id",
        controls=[
            ft.AppBar(
                title=ft.Text("Institutions Management"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/admin/{admin_id}")),
            ),
            ft.ListView(
                controls=[
                    institutions_table,
                ],
                auto_scroll=True,
                padding=20,
                spacing=10,
                expand=True,
                adaptive=True
            ),
            add_institution_button,
            dialog
        ],
        bgcolor=FG,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START
    )
