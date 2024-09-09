import flet as ft
from flet_route import Params, Basket
from views.conections import get_messages, send_message, create_connection,get_user

FG = '#B7C1F3'
BG = '#8C81BF'


def Chat_view_sup(page: ft.Page, params: Params, basket: Basket):

    page.title = 'Chat'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 600

    supervisor_id = int(params.get('my_id'))
    teacher_id = int(params.get('teacher_id'))

    def load_messages():
        messages = get_messages(supervisor_id, teacher_id)
        message_controls = []
        print(messages)
        for message in messages:
            is_teacher = message['id_sender'] == teacher_id
            alignment = ft.alignment.center_left if is_teacher else ft.alignment.center_right
            bg_color = "#E0E0E0" if is_teacher else "#D1C4E9"
            sender = "Teacher" if is_teacher else "You"

            message_controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(sender, size=10, color="#757575"),
                            ft.Container(
                                content=ft.Text(message['content']),
                                padding=10,
                                bgcolor=bg_color,
                                border_radius=10  
                            ),
                            ft.Text(f"{message['date']} {message['time']}", size=10, color="#757575")
                        ],
                        tight=True,
                        spacing=5
                    ),
                    alignment=alignment,
                    padding=10,
                    expand=False
                )
            )
        mark_messages_as_read(supervisor_id, teacher_id)
        return message_controls

    def send_message_callback(e):
        send_message(supervisor_id, teacher_id, message_input.value)
        message_input.value = ""
        messages_list.controls = load_messages()
        messages_list.update()
        page.update()

    def mark_messages_as_read(supervisor_id, teacher_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE messaging
            SET status = 1
            WHERE id_receiver = %s AND id_sender = %s AND status = 0
        ''', (supervisor_id, teacher_id))
        conn.commit()
        conn.close()

    message_input = ft.TextField(label="Write a message", expand=True)
    messages_list = ft.ListView(
        controls=load_messages(),
        expand=True
    )

    user = get_user(teacher_id)

    return ft.View(
        f"/chat_supervisor/chat/{supervisor_id}/{teacher_id}",
        controls=[
            ft.AppBar(
                title=ft.Text(user['full_name'], weight=ft.FontWeight.BOLD, size=12),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/chat_supervisor/{supervisor_id}")),
                automatically_imply_leading=False
            ),
            messages_list,
            ft.Row(
                controls=[
                    message_input,
                    ft.IconButton(icon=ft.icons.SEND, on_click=send_message_callback)
                ],
                spacing=10
            )
        ],
        bgcolor=FG
    )
