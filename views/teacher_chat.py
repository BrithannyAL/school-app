import flet as ft
from flet_route import Params, Basket
from views.conections import get_chats_teacher, delete_chat, get_available_supervisors

FG = '#B7C1F3'
BG = '#8C81BF'
CB = "#D1C4E9"
NOTIFICATION_COLOR = "#FF4081"  # Color for unread message notifications

def Chat_teacher(page: ft.Page, params: Params, basket: Basket):

    page.title = 'Chat'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 600

    teacher_id = int(params.get('my_id'))

    def open_chat(supervisor_id):
        page.go(f"/teacher_chat/chat_view/{teacher_id}/{supervisor_id}")
 
    def close_yes_dlg(e):  #Evento cerrar el dialogo de confirmacion
        page.close_dialog()
        dlg.data.confirm_dismiss(True)

    def close_no_dlg(e): #Evento para cancelar
        page.close_dialog()
        dlg.data.confirm_dismiss(False)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to delete this chat?"),
        actions=[
            ft.TextButton("Yes", on_click=close_yes_dlg),
            ft.TextButton("No", on_click=close_no_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    def handle_confirm_dismiss(e: ft.DismissibleDismissEvent):
        # Maneja la confirmación de deslizamiento para eliminar
        if e.direction == ft.DismissDirection.END_TO_START:  # Deslizamiento de derecha a izquierda
            dlg.data = e.control
            page.show_dialog(dlg)

    def handle_dismiss(e):
        #elimina el chat
        delete_chatAct(e.control.key)
        page.update()

    def handle_update(e: ft.DismissibleUpdateEvent):
        print(f"Update - direction: {e.direction}, progress: {e.progress}, reached: {e.reached}, previous_reached: {e.previous_reached}")

    def load_chats():
        chats = get_chats_teacher(teacher_id)
        chats_list.controls.clear()
        if not chats:
            chats_list.controls.append(
                ft.Text("No chats available", color=BG, size=15, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
            )
        else:
            for chat in chats:
                unread_indicator = None  # Indicador de mensajes no leídos
                if chat['unread_count'] == 0: #TODO CAMBIAR EL == por >, esta con el igual para acomodar el diseño
                    unread_indicator = ft.Container(
                        content=ft.Text(str(chat['unread_count']), size=10, color="white"),
                        width=20,
                        height=20,
                        bgcolor="red",
                        border_radius=10,
                        alignment=ft.alignment.center,
                        visible=chat['unread_count'] is not None
                    )
                else:
                    unread_indicator = ft.Container()

                chat_tile = ft.Dismissible(
                    key=str(chat['supervisor_id']),
                    on_dismiss=handle_dismiss,
                    on_update=handle_update,
                    on_confirm_dismiss=handle_confirm_dismiss,
                    dismiss_direction=ft.DismissDirection.END_TO_START, #Solo de derecha a izquierda
                    dismiss_thresholds={
                        ft.DismissDirection.END_TO_START: 0.2,
                    },
                    secondary_background=ft.Container(
                        bgcolor=ft.colors.RED,
                        alignment=ft.alignment.center_right,
                        content=ft.IconButton(
                            icon=ft.icons.DELETE
                        )
                    ),
                    content=ft.ListTile(
                        leading=ft.CircleAvatar(content=ft.Text(chat['name'][0]), bgcolor=BG),
                        title=ft.Text(f"{chat['name']} {chat['last_name']}", weight=ft.FontWeight.BOLD, size=14, color="black"),
                        subtitle=ft.Text(chat['last_message'], size=12, italic=True, color="black"),
                        trailing=ft.Column(
                            controls=[
                                unread_indicator,
                                ft.Text(chat['last_time'], size=12, color="black")
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=3
                        ),
                        on_click=lambda e, supervisor_id=chat['supervisor_id']: open_chat(supervisor_id),
                        is_three_line=True,
                    )
                )
                chats_list.controls.append(chat_tile)
        page.update()

    def confirm_delete_chat(supervisor_id):
        delete_dialog.content = ft.Text("Are you sure you want to delete this chat?")
        delete_dialog.actions = [
            ft.ElevatedButton(text="Delete", on_click=lambda e: delete_chatAct(supervisor_id)),
            ft.OutlinedButton(text="Cancel", on_click=lambda e: cancel_delete())
        ]
        delete_dialog.open = True
        page.update()

    def delete_chatAct(supervisor_id):
        delete_chat(supervisor_id, teacher_id)
        delete_dialog.open = False
        load_chats()

    def cancel_delete():
        delete_dialog.open = False
        page.update()

    delete_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Chat"),
    )

    def start_chat():
        supervisor_id = supervisor_dropdown.value
        if supervisor_id:
            open_chat(supervisor_id)
            new_chat_dialog.open = False
            page.update()

    def show_new_chat_dialog():
        new_chat_dialog.open = True
        page.update()

    supervisors = get_available_supervisors(teacher_id)
    supervisor_dropdown = ft.Dropdown(
        label="Supervisor",
        options=[
            ft.dropdown.Option(str(super['supervisor_id']), super['name'] + ' ' + super['last_name'])
            for super in supervisors
        ],
        width=300,
        on_change=lambda e: page.update()
    )

    new_chat_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("New Chat"),
        content=ft.Column(
            [
                ft.Text("Select a supervisor to start a new chat"),
                supervisor_dropdown
            ]
        ),
        actions=[
            ft.ElevatedButton(text="Add Chat", on_click=lambda e: start_chat()),
            ft.OutlinedButton(text="Cancel", on_click=lambda e: cancel())
        ]
    )

    def cancel():
        new_chat_dialog.open = False
        page.update()

    chats_list = ft.Column(
        controls=[],
        spacing=10,
        tight=True,
        expand=True
    )

    load_chats()

    return ft.View(
        "/teacher_chat",
        controls=[
            ft.AppBar(
                title=ft.Text("Chats"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/teacher/{teacher_id}")),
                automatically_imply_leading=False
            ),
            ft.Container(
                content=chats_list,
                expand=True
            ),
            ft.FloatingActionButton(
                icon=ft.icons.ADD,
                on_click=lambda e: show_new_chat_dialog()
            ),
            delete_dialog,
            new_chat_dialog
        ],
        bgcolor=FG
    )
