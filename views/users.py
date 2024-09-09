import flet as ft
from flet_route import Params, Basket
import sqlite3 as sql
import re
import mysql.connector
from .conections import create_connection

FG = '#B7C1F3'
BG = '#8C81BF'

def Users(page: ft.Page, params: Params, basket: Basket):

    # Vista de la pagina de usuarios
    page.title = 'Users Management'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 550
    # Extraer el valor de my_id
    admin_id = int(params.get('my_id'))

    # Funcion para obtener los usuarios de la base de datos
    def fetch_users():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        conn.close()
        return users

    # Funcion para añadir un nuevo usuario
    def add_user(name, last_name, email, password, user_type, specialty=None):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (name, last_name, email, password, user_type) VALUES (%s, %s, %s, %s, %s)", 
                       (name, last_name, email, password, user_type))
        new_user_id = cursor.lastrowid
        
        if user_type == 'teacher':
            cursor.execute("INSERT INTO teacher (id_teacher, specialty) VALUES (%s, %s)", (new_user_id, specialty))
        
        conn.commit()
        conn.close()
        refresh_users_table()
        show_confirmation_snackbar("User added successfully.")

    # Funcion para editar un usuario existente
    def edit_user(user_id, name, last_name, email, password, user_type, specialty=None):
        #conn = sql.connect('./db/database.db')
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET name = %s, last_name = %s, email = %s, password = %s, user_type = %s WHERE id_user = %s", 
                       (name, last_name, email, password, user_type, user_id))
        
        if user_type == 'teacher':
            cursor.execute("UPDATE teacher SET specialty = %s WHERE id_teacher = %s", (specialty, user_id))
        conn.commit()
        conn.close()
        refresh_users_table()        
        show_confirmation_snackbar("User updated successfully.")

    # Funcion para eliminar un usuario
    def delete_user(user_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teacher WHERE id_teacher = %s", (user_id,))
        cursor.execute("DELETE FROM user WHERE id_user = %s", (user_id,))
        conn.commit()
        conn.close()
        refresh_users_table()
        show_confirmation_snackbar("User deleted successfully.")

    # Refrescar la tabla de usuarios
    def refresh_users_table():
        users = fetch_users()
        users_table.rows.clear()
        users_table.rows.extend([
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(user[0]), color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(user[1], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(user[2], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(user[3], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(user[5], color=ft.colors.BLACK)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, user=user: open_edit_user_dialog(user)),
                                ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, user=user: delete_user(user[0]))
                            ]
                        )
                    )
                ]
            )
            for user in users
        ])
        page.update()

    # Mostrar snackbar de confirmación
    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    # Abrir el dialogo para añadir un nuevo usuario
    def open_add_user_dialog(e):
        dialog.open = True
        dialog_title.value = "Add User"
        name_input.value = ""
        last_name_input.value = ""
        email_input.value = ""
        password_input.value = ""
        user_type_input.value = None
        specialty_input.value = ""
        specialty_input.visible = False
        save_button.on_click = save_new_user
        save_button.disabled = True  # Inicialmente deshabilitado
        cancel_button.on_click = cancel
        page.update()

    # Guardar el nuevo usuario
    def save_new_user(e):
        add_user(name_input.value, last_name_input.value, email_input.value, password_input.value, user_type_input.value, specialty_input.value)
        dialog.open = False
        page.update()

    # Cancelar
    def cancel(e):
        dialog.open = False
        page.update()

    # Abrir el dialogo para editar un usuario
    def open_edit_user_dialog(user):
        dialog.open = True
        dialog_title.value = "Edit User"
        name_input.value = user[1]
        last_name_input.value = user[2]
        email_input.value = user[3]
        password_input.value = user[4]
        user_type_input.value = user[5] if len(user) > 5 else ""
        specialty_input.value = fetch_teacher_specialty(user[0]) if user[5] == 'teacher' else ""
        specialty_input.visible = (user[5] == 'teacher')
        save_button.on_click = lambda e: save_edited_user(user[0])
        save_button.disabled = False  # Habilitado cuando editamos un usuario existente
        cancel_button.on_click = cancel
        page.update()

    # Obtener la especialidad del profesor
    def fetch_teacher_specialty(teacher_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT specialty FROM teacher WHERE id_teacher = %s", (teacher_id,))
        specialty = cursor.fetchone()
        conn.close()
        return specialty[0] if specialty else ""

    # Guardar los cambios del usuario editado
    def save_edited_user(user_id):
        edit_user(user_id, name_input.value, last_name_input.value, email_input.value, password_input.value, user_type_input.value, specialty_input.value)
        dialog.open = False
        page.update()

    # Validar campos
    def validate_fields(e):
        name_valid = bool(name_input.value.strip())
        last_name_valid = bool(last_name_input.value.strip())
        email_valid = bool(re.match(r"[^@]+@[^@]+\.[^@]+", email_input.value.strip()))
        password_valid = bool(password_input.value.strip())
        user_type_valid = user_type_input.value is not None
        specialty_valid = specialty_input.visible and specialty_input.value.strip() != "" or not specialty_input.visible

        if not name_valid:
            name_input.error_text = "Name cannot be empty."
        else:
            name_input.error_text = None
        
        if not last_name_valid:
            last_name_input.error_text = "Last Name cannot be empty."
        else:
            last_name_input.error_text = None
        
        if not email_valid:
            email_input.error_text = "Invalid email format."
        else:
            email_input.error_text = None
        
        if not password_valid:
            password_input.error_text = "Password cannot be empty."
        else:
            password_input.error_text = None

        if specialty_input.visible and not specialty_valid:
            specialty_input.error_text = "Specialty cannot be empty."
        else:
            specialty_input.error_text = None

        save_button.disabled = not (name_valid and last_name_valid and email_valid and password_valid and user_type_valid and specialty_valid)
        page.update()

    # Manejar el cambio del tipo de usuario
    def handle_user_type_change(e):
        specialty_input.visible = (user_type_input.value == 'teacher')
        validate_fields(e)

    # Componentes del dialogo de usuario
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(),
        content=ft.Column(
            [
                ft.TextField(label="Name", on_change=validate_fields),
                ft.TextField(label="Last Name", on_change=validate_fields),
                ft.TextField(label="Email", on_change=validate_fields),
                ft.TextField(label="Password", on_change=validate_fields),
                ft.Dropdown(
                    label="Role",
                    width=100,
                    options=[
                        ft.dropdown.Option("administrator"),
                        ft.dropdown.Option("teacher"),
                        ft.dropdown.Option("supervisor"),
                    ],
                    on_change=handle_user_type_change
                ),
                ft.TextField(label="Specialty", visible=False, on_change=validate_fields)
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
    last_name_input = dialog.content.controls[1]
    email_input = dialog.content.controls[2]
    password_input = dialog.content.controls[3]
    user_type_input = dialog.content.controls[4]
    specialty_input = dialog.content.controls[5]
    save_button = dialog.actions[0]
    cancel_button = dialog.actions[1]

    # Tabla de usuarios
    users_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Name", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Last Name", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Email", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Role", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Actions", color=ft.colors.BLACK))
        ],
        rows=[],
        column_spacing=15,
        data_row_color=ft.colors.WHITE,
        heading_row_color=BG
    )

    # Boton para añadir un nuevo usuario
    add_user_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_user_dialog)

    refresh_users_table()

    # Vista de la pagina de usuarios
    return ft.View(
        "/users",
        controls=[
            ft.AppBar( # Barra de navegacion
                title=ft.Text("Users Management"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/admin/{admin_id}")),
            ),
            ft.ListView(
                controls=[
                    users_table,
                ],
                auto_scroll=True,
                padding=20,
                spacing=10,
                expand=True,
                adaptive=True
            ),
            add_user_button,
            dialog
        ],
        bgcolor=FG,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START
    )
