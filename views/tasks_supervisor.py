import flet as ft
from flet_route import Params, Basket
from views.conections import create_connection
import pyrebase

def Tasks_supervisor(page: ft.Page, params: Params, basket: Basket):

    page.title = 'View tasks'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 500
    page.window_height = 700

    FG = '#B7C1F3'
    BG = '#8C81BF'

    supervisor_id = int(params.get('my_id'))

    def fetch_student():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT s.id_student, s.id_group, s.name, s.last_name
                            FROM student s INNER JOIN supervisor sp ON s.id_student = sp.id_student
                            WHERE sp.id_user = %s""", (supervisor_id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        return student

    student = fetch_student()

    def fetch_task():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT t.id_task, t.title, t.description, t.start_date, t.due_date, ta.status
                            FROM task t INNER JOIN task_assignment ta ON t.id_task = ta.id_task
                            WHERE ta.id_student = %s""", (student[0],))
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        return tasks

    tasks = fetch_task()

    def fetch_files(id_task):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT f.id_file, f.file
                            FROM task t INNER JOIN files f ON t.id_task = f.id_task
                            WHERE t.id_task = %s""", (id_task,))
        files = cursor.fetchall()
        cursor.close()
        conn.close()
        return files

    def handle_change(e: ft.ControlEvent):
        print(f"change on panel with index {e.data}")

    panel = ft.ExpansionPanelList(
        expand_icon_color=BG,
        elevation=8,
        divider_color=BG,
        on_change=handle_change,
        controls=[]
    )

    def download_file(file_id, name_file):
        config = {
            "apiKey": "AIzaSyCjfGr6ecemiXiWRQKObHitLvCsSfWJ-4s",
            "authDomain": "schoolapp-a4b24.firebaseapp.com",
            "projectId": "schoolapp-a4b24",
            "storageBucket": "schoolapp-a4b24.appspot.com",
            "messagingSenderId": "9462975580",
            "appId": "1:9462975580:web:5baa9fa04c7ce41b452a99",
            "measurementId": "G-V9KC8L6905",
            "service_account": "service_account.json",
            "databaseURL": "https://schoolapp-a4b24-default-rtdb.firebaseio.com/"
        }

        firebase = pyrebase.initialize_app(config)
        storage = firebase.storage()

        storage.download(str(file_id), str(name_file))  # El nombre del archivo en la nube y el nombre con el que se quiere descargar

    def create_task_view(task):
        files = fetch_files(task[0])
        exp = ft.ExpansionPanel(
            bgcolor=BG,
            header=ft.ListTile(
                title=ft.Text(task[1], weight=ft.FontWeight.BOLD)
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"Description: {task[2]}", color=ft.colors.BLACK, size=14, weight=ft.FontWeight.NORMAL),
                        ft.Text(f"Start Date: {task[3]}", color=ft.colors.BLACK, size=14, weight=ft.FontWeight.NORMAL),
                        ft.Text(f"Due Date: {task[4]}", color=ft.colors.BLACK, size=14, weight=ft.FontWeight.NORMAL),
                        ft.Text(f"Status: {task[5]}", color=ft.colors.BLACK, size=14, weight=ft.FontWeight.NORMAL),
                        ft.Text("Files:", color=ft.colors.BLACK, size=14, weight=ft.FontWeight.BOLD),
                        ft.Column(
                            controls=[
                                ft.Container(
                                    content=ft.TextButton(
                                        text=file[1],
                                        on_click=lambda e, file_id=file[0], name_file=file[1]: download_file(file_id, name_file),
                                    ),
                                    padding=ft.padding.only(bottom=5)
                                ) for file in files
                            ]
                        )
                    ],
                    spacing=10,
                    auto_scroll=True
                ),
                padding=ft.padding.all(10)
            ),
            expanded=False
        )
        return exp

    for task in tasks:
        panel.controls.append(create_task_view(task))

    return ft.View(
        "/tasks_supervisor",
        controls=[
            ft.AppBar(
                title=ft.Text("Tasks to do"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/panel_supervisor/{supervisor_id}")),
                automatically_imply_leading=False
            ),
            ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(student[2] + " " + student[3], size=20, weight=ft.FontWeight.BOLD),
                        padding=ft.padding.only(bottom=20)
                    ),
                    panel  # Agregamos el panel directamente aquí
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
                auto_scroll=True
            )
        ],
        bgcolor=FG,
        padding=ft.padding.all(20),
        adaptive=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
