import flet as ft
from flet_route import Params, Basket
import pyrebase
from .conections import create_connection

def Task(page:ft.Page, params : Params, basket: Basket):
    
    page.title = 'Create Task'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 600
    page.window_height = 500

    FG = '#B7C1F3'
    BG = '#8C81BF'

    teacher_id = int(params.get('my_id'))

    #Crear una vista para todos los grupos de este profesor
    def fetch_tasks():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task WHERE id_teacher = %s", (teacher_id,))
        groups = cursor.fetchall()
        conn.close()
        return groups
    

    # Lista para ver las tareas
    task_list = ft.ExpansionPanelList()

    # Refrescar la lista de tareas
    def refresh_table():
        tasks = fetch_tasks()
        task_list.controls.clear()
        if tasks:
            task_list.controls.extend([
                ft.ExpansionPanel(
                    header=ft.Text(task[1], weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                    content=ft.Column(
                        controls=[
                            ft.Text(f"ID: {task[0]}"),
                            ft.Text(f"Description: {task[2]}", color=ft.colors.BLACK),
                            ft.Text(f"Start date: {task[3]}", color=ft.colors.BLACK),
                            ft.Text(f"Due Date: {task[4]}", color=ft.colors.BLACK),
                            ft.Row(
                                controls=[
                                    ft.IconButton(ft.icons.DELETE, on_click=lambda e, task_id=task[0]: confirm_delete(task_id)),
                                    ft.IconButton(ft.icons.EDIT, on_click=lambda e, task_info=task: edit_task_dialog(task_info)),
                                    ft.IconButton(ft.icons.ATTACH_FILE, on_click=lambda e, task_id=task[0]: open_file_picker(task_id)),
                                ]
                            ),
                            ft.TextButton("View Files", on_click=lambda e, task_id=task[0]: view_files_dialog(task_id),
                                          disabled=not check_files_exist(task[0])),
                        ],
                        spacing=10
                    ),
                )
                for task in tasks
            ])
        else:
            show_confirmation_snackbar("No tasks available.")
        page.update()
    

    '''#tabla para ver las tareas
    task_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Title", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Description", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Start date", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Due Date", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Actions", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("File", color=ft.colors.BLACK))
        ],
        rows=[],
        column_spacing=15,
        data_row_color=ft.colors.WHITE,
        heading_row_color=BG,
        data_row_max_height=100
    )

    #refrescar la tabla de tareas
    def refresh_table():
        tasks = fetch_tasks()
        task_table.rows.clear()
        if tasks:
            task_table.rows.extend([
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(tasks[0]), color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(tasks[1], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(tasks[2], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(tasks[3], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(tasks[4], color=ft.colors.BLACK)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(ft.icons.DELETE, on_click=lambda e, task_id=tasks[0]: confirm_delete(task_id)),
                                    ft.IconButton(ft.icons.EDIT, on_click=lambda e, task_info=tasks: edit_task_dialog(task_info)),
                                    ft.IconButton(ft.icons.ATTACH_FILE, on_click=lambda e, task_id=tasks[0]: open_file_picker(task_id))
                                ]
                            )
                        ),
                        ft.DataCell(ft.TextButton(text="View Files", on_click=lambda e, task_id=tasks[0]: view_files_dialog(task_id),
                                disabled=not check_files_exist(tasks[0])
                            )
                        )
                    ]
                )
                for tasks in tasks
            ])
        else:
            show_confirmation_snackbar("No tasks available.")      
        page.update()'''

    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def check_files_exist(task_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files WHERE id_task = %s", (task_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0

    def add_task(title, descrip, stDate, duDate):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO task (title, description, start_date, due_date, id_teacher) VALUES (%s, %s, %s, %s, %s)", (title, descrip, stDate, duDate, teacher_id))
        conn.commit()
        conn.close()
        refresh_table()

    # Crear la ventana emergente
    def open_add_task_dialog(e):
        title_input = ft.TextField(label="Title")
        description_input = ft.TextField(label="Description")
        start_date_input = ft.TextField(label="Start Date (d/m/y)")
        due_date_input = ft.TextField(label="Due Date (d/m/y)")
        
        error_message = ft.Text(color=ft.colors.RED, visible=False)
        
        def validate_and_add_task(e):
            if not title_input.value or not description_input.value or not start_date_input.value or not due_date_input.value:
                error_message.value = "All fields are required."
                error_message.visible = True
                page.update()
            else:
                add_task(
                    title_input.value,
                    description_input.value,
                    start_date_input.value,
                    due_date_input.value
                )
                dialog.open = False
                page.update()
                error_message.visible = False

        dialog = ft.AlertDialog(
            title=ft.Text("Add Task"),
            content=ft.Column([
                title_input,
                description_input,
                start_date_input,
                due_date_input,
                error_message
            ]),
            actions=[
                ft.TextButton("Add", on_click=validate_and_add_task),
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False))
            ],
            open=True
        )
        page.dialog = dialog
        page.update()
        

    def delete_task(id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task WHERE id_task = %s", (id,))
        conn.commit()
        conn.close()
        refresh_table()

    def confirm_delete(task_id):
        def delete_and_close(e):
            delete_task(task_id)
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text("Are you sure you want to delete this task?"),
            actions=[
                ft.TextButton("Delete", on_click=delete_and_close),
                ft.TextButton("Cancel", on_click=lambda _: setattr(dialog, 'open', False))
            ],
            open=True
        )
        page.dialog = dialog
        page.update()

    def edit_task(title, descrip, stDate, DuDate, id_task):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE task SET title = %s, description = %s, start_date = %s, due_date = %s WHERE id_task = %s", (title, descrip, stDate, DuDate, id_task))
        conn.commit()
        conn.close()
        refresh_table()

    def edit_task_dialog(task_info):
        title_input = ft.TextField(label="Title", value=task_info[1])
        description_input = ft.TextField(label="Description", value=task_info[2])
        start_date_input = ft.TextField(label="Start Date (d/m/y)", value=task_info[3])
        due_date_input = ft.TextField(label="Due Date (d/m/y)", value=task_info[4])

        def update_task(e):
            edit_task(
                title_input.value,
                description_input.value,
                start_date_input.value,
                due_date_input.value,
                task_info[0]  # task_id
            )
            dialog.open = False
            page.update()
            refresh_table()

        dialog = ft.AlertDialog(
            title=ft.Text("Edit Task"),
            content=ft.Column([
                title_input,
                description_input,
                start_date_input,
                due_date_input,
            ]),
            actions=[
                ft.TextButton("Update", on_click=update_task),
                ft.TextButton("Cancel", on_click=lambda _: setattr(page, 'dialog', False))
            ],
            open=True
        )
        page.dialog = dialog
        page.update()

    def open_file_picker(task_id):
        def file_selected(e):
            if file_picker.result.files:
                selected_file = file_picker.result.files[0]
                selected_file_path = selected_file.path
                selected_file_name = selected_file.name
                print(f"Archivo seleccionado para la tarea {task_id}: {selected_file_name} ({selected_file_path})")
                add_file(task_id, selected_file_name, selected_file_path)

        file_picker.on_result = file_selected
        file_picker.pick_files(allow_multiple=False)
        page.update()

    def get_id_file(task_id, name_file):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_file FROM files WHERE id_task = %s AND file = %s", (task_id, name_file))
        id_file = cursor.fetchone()
        conn.close()
        return id_file[0]

    def add_file(task_id, name_file, path_file):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (id_task, file) VALUES (%s, %s)", (task_id, name_file))
        conn.commit()
        conn.close()
        id_file = get_id_file(task_id, name_file)
        firebase_push(path_file, id_file)

    def firebase_push(path_file, id_file):
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

        storage.child(str(id_file)).put(path_file) # Subir archivo con el nombre que va a tener en la base de datos y luego el file_path

    def view_files_dialog(task_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file FROM files WHERE id_task = %s", (task_id,))
        files = cursor.fetchall()
        conn.close()

        files_list = ft.Column(
            [ft.Text(f[0]) for f in files],
            spacing=10
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Files"),
            content=files_list,
            actions=[
                ft.TextButton("Close", on_click=close_dialog)
            ],
            open=True
        )
        page.dialog = dialog
        page.update()

    # Crear el FilePicker y añadirlo a la página
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    refresh_table()

    #En el return se muestra la vista
    return ft.View(
        "/tasks",
        controls=[
            ft.AppBar(
                title=ft.Text("Create Task"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/teacher/{teacher_id}")),
                automatically_imply_leading=False
            ),
            ft.ListView(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                task_list
                            ],
                        ),
                        padding=ft.padding.all(10),
                        alignment=ft.alignment.center,
                    )
                ],
                auto_scroll=True,
                expand=True,
                adaptive=True,
                padding=ft.padding.all(10),
            ),
            ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_task_dialog)
        ],
        bgcolor=FG,
        padding=ft.padding.all(20),
        adaptive=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )