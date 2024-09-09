import flet as ft
from flet_route import Params, Basket
from views.conections import create_connection

#TODO Aqui va el panel del profesor 

def Teacher(page:ft.Page, params : Params, basket: Basket):

    page.title = 'Teacher View'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 600

    FG = '#B7C1F3'
    BG = '#8C81BF'

    #Extraer el valor del id
    teacher_id = int(params.get('my_id'))

    #Tarjetas con icono y texto 
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
            badge = ft.Container() #contenedor vacío

        return ft.Row(
            [
                ft.GestureDetector(
                    content=ft.Row(
                        [
                            ft.Icon(name=icon, size=40),
                            badge
                        ]
                    ),
                    on_tap=lambda _: page.go(route)
                ),
                ft.Text(label, size=16)
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )
    
    def get_unread_messages_count(teacher_id):
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT COUNT(*) as unread_count
            FROM messaging
            WHERE id_receiver = %s AND status = 0
        ''', (teacher_id,))
        result = cursor.fetchone()
        print(result)
        conn.close()
        return result['unread_count']
    
    #Datos de los elementos del panel del profesor
    teacher_items = [
        ("ADD_TASK_OUTLINED", "All Tasks",f"/tasks/{teacher_id}", 0),
        ("ASSIGNMENT_ADD", "Assign task", f"/assign_task/{teacher_id}", 0),
        ("CHAT", "Chats with supervisor", f"/teacher_chat/{teacher_id}", get_unread_messages_count(teacher_id))
    ]

    teacher_cards = [create_card(icon, label, route, badge_count) for icon, label, route, badge_count in teacher_items]

    #En el return se muestra la vista
    return ft.View(
        "/teacher",
        controls=[
                ft.AppBar( #Barra de navegacion
                    title=ft.Text("Teacher Panel"),
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
                                    ft.Text("Options", size=16, color="white")
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
                            controls=teacher_cards,
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
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
