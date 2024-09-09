import flet as ft
from flet_route import Params, Basket
#import sqlite3 as sql
import mysql.connector 
from mysql.connector import Error
from .conections import create_connection

FG = '#B7C1F3'


def Login(page: ft.Page, params: Params, basket: Basket):
    # Vista del login
    page.title = 'Login'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 600
    
    # Ruta de la imagen del logo
    logo_image_path = "assets/login.png"  # Actualiza esta ruta según corresponda

    # Datos del usuario 
    email_input = ft.TextField(label="Email", width=300, icon=ft.icons.PERSON, on_change=lambda e: validate())
    password_input = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True, icon=ft.icons.LOCK, on_change=lambda e: validate())
    login_button = ft.ElevatedButton("Sign In", style=ft.ButtonStyle(
        #padding=ft.Padding(15, 30, 15, 30),
        shape=ft.RoundedRectangleBorder(radius=30)),
        disabled=True,
        on_click=lambda _: handle_login_click())
    register_button = ft.ElevatedButton("Registrarse", on_click=lambda _: page.go("/registerIns/10")) # Cambiar el id
    
    error_text = ft.Text("", size=20, color="red")
    
    # Se valida que haya datos en la entrada de texto
    def validate():
        login_button.disabled = not (email_input.value and password_input.value)
        page.update()

    def handle_login_click():
        email = email_input.value
        password = password_input.value
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
            result = cursor.fetchone()
            if result:
                id = result[0]
                role = result[5]
                match role:
                    case "administrator":
                        page.go(f"/admin/{id}")
                    case "teacher":
                        page.go(f"/teacher/{id}")
                    case "supervisor":
                        page.go(f"/panel_supervisor/{id}")
            else:
                error_text.value = "*Invalid credentials"
                page.update()
        except Error as err: #Se cambió a los errores de la base de datos en clever cloud
            error_text.value = f"Database error: {str(err)}"
            print(str(err))
            page.update()
        finally:
            conn.close()

    return ft.View(
        "/",
        controls=[
            ft.Column(
                [
                    ft.Image(src=logo_image_path, width=100, height=100, visible=True), 
                    ft.Text("login", size=30, weight="bold"),
                    ft.Text("Please login to use the platform", size=14, color="#0A0E3F"),
                    email_input,
                    password_input,
                    login_button,
                    register_button,
                    error_text,
                
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        ],
        bgcolor=FG,
        padding=ft.padding.all(20),
        adaptive=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

