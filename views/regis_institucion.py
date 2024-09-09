import flet as ft
from flet_route import Params, Basket
import sqlite3 as sql
import re
import mysql.connector
from .conections import create_connection
FG = '#B7C1F3'
BG = '#8C81BF'

def Regis_institucion(page: ft.Page, params: Params, basket: Basket):

    # Vista de la página de registro de instituciones
    page.title = 'Register Institution'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 520

    # Inserción en la base de datos
    def insert_institution(name, address, telephone, email, admin_name, admin_last_name, admin_email, admin_password):
        conn = create_connection()
        cursor = conn.cursor()
        #Se inserta el administrador
        cursor.execute('''
        INSERT INTO user (name, last_name, email, password, user_type)
        VALUES (%s, %s, %s, %s, 'administrator')
        ''', (admin_name, admin_last_name, admin_email, admin_password))
        admin_id = cursor.lastrowid

        #Se inserta la intitucion
        cursor.execute('''
        INSERT INTO institution (name, address, telephone, email, id_administrator)
        VALUES (%s, %s, %s, %s, %s)
        ''', (name, address, telephone, email, admin_id))
        
        conn.commit()
        conn.close()

    # Validar campos
    def validate_fields(e):
        all_filled = all(field.value.strip() for field in fields)
        valid_format = all([
            len(fields[2].value) == 8 and fields[2].value.isdigit(),  # Teléfono
            re.match(r"[^@]+@[^@]+\.[^@]+", fields[3].value.strip()),  # Email institución
            re.match(r"[^@]+@[^@]+\.[^@]+", fields[6].value.strip()),  # Email administrador
        ])
        
        # Mostrar mensajes de error si no cumplen con los formatos
        fields[2].error_text = None if len(fields[2].value) == 8 and fields[2].value.isdigit() else "Phone number must be 8 digits."
        fields[3].error_text = None if re.match(r"[^@]+@[^@]+\.[^@]+", fields[3].value.strip()) else "Invalid email format."
        fields[6].error_text = None if re.match(r"[^@]+@[^@]+\.[^@]+", fields[6].value.strip()) else "Invalid email format."

        submit_button.disabled = not (all_filled and valid_format)
        page.update()

    # Función para manejar el envío del formulario
    def on_submit(e):
        # Extraer valores de los campos
        institution_name = fields[0].value
        institution_address = fields[1].value
        institution_telephone = fields[2].value
        institution_email = fields[3].value
        admin_name = fields[4].value
        admin_last_name = fields[5].value
        admin_email = fields[6].value
        admin_password = fields[7].value
        # Insertar en la base de datos
        insert_institution(institution_name, institution_address, institution_telephone, institution_email,
                           admin_name, admin_last_name, admin_email, admin_password)

        # Mostrar mensaje
        show_confirmation_snackbar("Institution registered successfully.")
        page.go("/")  # Redirigir al login

    # Función para manejar la cancelación del formulario
    def on_cancel(e):
        page.go("/")

    # Mostrar snackbar de confirmación
    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    fields = [
        ft.TextField(label="Institution Name", on_change=validate_fields),
        ft.TextField(label="Institution Address", on_change=validate_fields),
        ft.TextField(label="Institution Telephone", on_change=validate_fields),
        ft.TextField(label="Institution Email", on_change=validate_fields),
        ft.TextField(label="Administrator Name", on_change=validate_fields),
        ft.TextField(label="Administrator Last Name", on_change=validate_fields),
        ft.TextField(label="Administrator Email", on_change=validate_fields),
        ft.TextField(label="Administrator Password", password=True, on_change=validate_fields)
    ]

    submit_button = ft.ElevatedButton("Submit", on_click=on_submit, disabled=True)
    cancel_button = ft.ElevatedButton("Cancel", on_click=on_cancel)

    return ft.View(
        "/registerIns/:my_id",
        controls=[
            ft.AppBar( #Barra de navegacion
                    title=ft.Text("Register Institution",text_align=ft.alignment.center),
                    bgcolor=BG,
                    automatically_imply_leading=False
                ),
            ft.Row(
                [
                    ft.Column(
                        [ft.Text("Institution Details", size=20, weight="bold")] + fields[:4],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        [ft.Text("Administrator Details", size=20, weight="bold")] + fields[4:],
                        alignment=ft.MainAxisAlignment.START
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND
            ),
            ft.Row(
                [
                    submit_button,
                    cancel_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND
            )
        ],
        spacing=10,
        bgcolor=FG
    )
