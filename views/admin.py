import flet as ft
from flet_route import Params, Basket
import sqlite3 as sql
import re

#TODO Agregar una vista con la info del admin
#TODO En la tabla de usuarios agregar un filter para el tipo de usuario

FG = '#B7C1F3'
BG = '#8C81BF'

def Admin(page: ft.Page, params: Params, basket: Basket):
    # Vista del panel de administración
    page.title = 'Admin'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 600
    page.window_height = 450

    # Extraer el valor de my_id
    admin_id = int(params.get('my_id'))

    # Función para crear tarjetas con icono y texto
    def create_card(icon, label, route):
        return ft.Column(
            [
                ft.GestureDetector(
                    content=ft.Stack(
                        [
                            ft.Icon(name=icon, size=40),
                        ]
                    ),
                    on_tap=lambda _: page.go(route)
                ),
                ft.Text(label, size=14)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

    # Datos de los elementos del panel de administración
    admin_items = [
        ("HOME_WORK_OUTLINED", "Institutions",f"/institutions/{admin_id}"), 
        ("PEOPLE_OUTLINED", "All Users",f"/users/{admin_id}"),
        ("CLASS_OUTLINED", "Groups",f"/groups/{admin_id}"),
        ("SCHOOL", "Students",f"/students/{admin_id}"),
        ("FAMILY_RESTROOM", "Supervisors",f"/supervisor/{admin_id}"),
    ]

    # Se rean las tarjetas a partir de los datos y las rutas
    admin_cards = [create_card(icon, label, route) for icon, label, route in admin_items]

    # Vista de la página de administrador
    return ft.View(
        "/admin",
        controls=[
                ft.AppBar( #Barra de navegacion
                    title=ft.Text("Admin Panel"),
                    bgcolor=BG,
                    actions=[
                        ft.IconButton( 
                            ft.icons.PERSON_OUTLINED,
                            on_click=lambda _: print("QUIERO VER MI PERFIL") #TODO Agregar una vista con la info del admin
                        ),
                        ft.IconButton( #salir 
                            ft.icons.EXIT_TO_APP,
                            on_click=lambda _: page.go("/")
                        ),
                    ],
                    automatically_imply_leading=False
                ),
                ft.GridView( #Opciones del menu
                    controls=admin_cards,
                    runs_count=3,
                    spacing=20,
                    run_spacing=20,
                    padding=20
                ),
        ],
        bgcolor=FG,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

