import flet as ft
from flet_route import Params, Basket
from views.conections import create_connection

def Panel_supervisor(page:ft.Page, params : Params, basket: Basket):

    page.title = 'Supervisor view'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 600

    FG = '#B7C1F3'
    BG = '#8C81BF'

    # Extraer el valor del id
    supervisor_id = int(params.get('my_id'))

    #Extraer el nombre del supervisor
    def fetch_name_supervisor():
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''SELECT name, last_name FROM user WHERE id_user = %s''', (supervisor_id,))
        result = cursor.fetchone()
        conn.close()
        name = result['name'] + " " + result['last_name']
        return name
    supervisor_name = fetch_name_supervisor()

    # Tarjetas con icono y texto
    def create_card(icon, label, route, badge_count):

        if badge_count > 0:
            badge = ft.Container(
                content=ft.Text(str(badge_count), size=12, color="white"),
                width=20,
                height=20,
                bgcolor="red",
                border_radius=10,
                alignment=ft.alignment.center,
                visible=badge_count is not None
            )
        else: 
            badge = ft.Container() # Contenedor vacío

        return ft.Row(
            [
                ft.GestureDetector(
                    content=ft.Row(
                        [
                            ft.Icon(name=icon, size=40),
                            badge
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    on_tap=lambda _: page.go(route)
                ),
                ft.Text(label, size=16)
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )
    
    def get_unread_messages_count(supervisor_id):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT COUNT(*) as unread_count
            FROM messaging
            WHERE id_receiver = %s AND status = 0
        ''', (supervisor_id,))
        result = cursor.fetchone()
        print(result)
        conn.close()
        return result['unread_count']
    
    # Datos de los elementos del panel del profesor
    supervisor_items = [
        ("TASK", "Student tasks", f"/tasks_supervisor/{supervisor_id}", 0),
        ("MESSAGE", "Teachers chats", f"/chat_supervisor/{supervisor_id}", get_unread_messages_count(supervisor_id)),
    ]

    supervisor_cards = [create_card(icon, label, route, badge_count) for icon, label, route, badge_count in supervisor_items]

    # En el return se muestra la vista
    return ft.View(
        "/panel_supervisor",
        controls=[
            ft.AppBar( #Barra de navegacion
                title=ft.Text("Supervisor Panel"),
                bgcolor=BG,
                actions=[
                    ft.IconButton( #salir 
                        ft.icons.EXIT_TO_APP,
                        on_click=lambda _: page.go("/")
                    ),
                ],
                automatically_imply_leading=False
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(supervisor_name, size=20, color="white")
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.START
                            ),
                            padding=30,
                            bgcolor=BG,
                            width=page.window_width,
                            alignment=ft.alignment.center,
                            margin=20,
                        ),
                        ft.Column(
                            controls=supervisor_cards,
                            spacing=30,
                            width=page.window_width - 30,
                            horizontal_alignment=ft.CrossAxisAlignment.START
                        )
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=20,
                bgcolor=FG
            )
        ],
        bgcolor=FG,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.START
    )
