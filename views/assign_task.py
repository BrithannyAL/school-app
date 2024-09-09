import flet as ft
import mysql.connector
from flet_route import Params, Basket
from .conections import create_connection

def Assign_task(page: ft.Page, params: Params, basket: Basket):

    page.title = 'Assign Task'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 900
    page.window_height = 700

    FG = '#B7C1F3'
    BG = '#8C81BF'

    teacher_id = int(params.get('my_id'))

    #Consultas a la base de datos
    def fetch_taks_id_title():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_task, title FROM task WHERE id_teacher = %s", (teacher_id,))
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        return tasks
    
    def fetch_group_id_name():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_group, name FROM students_group WHERE id_teacher = %s", (teacher_id,))
        groups = cursor.fetchall()
        cursor.close()
        conn.close()
        return groups
    
    def fetch_assigned_tasks():
        #conecto a la base de datos:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT DISTINCT sg.id_group, sg.name, t.id_task, t.title, t.start_date, t.due_date FROM students_group sg
                       JOIN student s ON sg.id_group = s.id_group
                       JOIN task_assignment ta ON s.id_student = ta.id_student
                       JOIN task t ON ta.id_task = t.id_task
                       WHERE sg.id_teacher = %s
                       ORDER BY sg.id_group, t.id_task;""", (teacher_id,)
                       )
        assigned_tasks = cursor.fetchall()
        print(assigned_tasks)
        cursor.close()
        conn.close()
        return assigned_tasks
    

    # Dropdowns para seleccionar tarea y grupo
    task_dropdown = ft.Dropdown(
        #TODO: HACER un cambio
        options=[ft.dropdown.Option(t[0], t[1]) for t in fetch_taks_id_title()],
        label="Select Task",
        width=300
    )

    group_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(g[0], g[1]) for g in fetch_group_id_name()],
        label="Select Group",
        width=300
    )

    # Definir el SnackBar
    snackbar = ft.SnackBar(
        content=ft.Text("Please select both a task and a group.", color=ft.colors.WHITE),
        bgcolor=ft.colors.RED
    )

    # Función para asignar tarea
    def assign_task(e):
        #Validar que los dropdown no tengan valores nulos
        if task_dropdown.value is None or group_dropdown.value is None:
            #Mostrar un mensaje de alerta
            page.snack_bar = snackbar
            snackbar.open = True
            page.update()    
        else:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_student FROM student WHERE id_group = %s", (group_dropdown.value,))
            students = cursor.fetchall()
            print(students)
            for student in students:
                cursor.execute("INSERT INTO task_assignment (id_student, id_task, status) VALUES (%s, %s, %s)",
                            (student[0], task_dropdown.value, 'Not Started'))
            conn.commit()
            conn.close()
            cursor.close()
            refresh_assigned_tasks_table()
            show_confirmation_snackbar("Task assigned successfully.")

    # Botón para asignar tarea
    assign_button = ft.ElevatedButton(
        text="Assign Task",
        on_click=assign_task,
        bgcolor=BG,
        color=ft.colors.WHITE,
        width=150
    )

    #Función para eliminar una asignación
    def delete_assignment(group_id, task_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM task_assignment WHERE id_task = %s
                        AND id_student IN (
                            SELECT id_student
                            FROM student
                            WHERE id_group = %s) """, (task_id, group_id))
        conn.commit()
        refresh_assigned_tasks_table()
        cursor.close()
        conn.close()

    assigned_task_list = ft.ExpansionPanelList()

    def refresh_assigned_tasks_table():
        assigned_tasks =  fetch_assigned_tasks()
        assigned_task_list.controls.clear()
        if assigned_tasks:
            assigned_task_list.controls.extend([
                ft.ExpansionPanel(
                    header=ft.Text(group_task[1], weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                    content=ft.Column(
                        controls=[
                            ft.Text(f"Assigned Task: {group_task[3]}", color=ft.colors.BLACK),
                            ft.Text(f"Start Date: {group_task[4]}", color=ft.colors.BLACK),
                            ft.Text(f"Due Date: {group_task[5]}", color=ft.colors.BLACK),
                            ft.Row(
                                controls=[
                                    ft.IconButton(ft.icons.DELETE, on_click=lambda e,
                                              task_id=group_task[2], group_id=group_task[0]: delete_assignment(group_id, task_id))
                                ]
                            )
                        ],
                        spacing=10
                    ),
                )
                for group_task in assigned_tasks
            ])
        else:
            show_confirmation_snackbar("No tasks assigned yet.")
        page.update()

    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    '''# Función para refrescar la tabla de tareas asignadas
    def refresh_assigned_tasks_table():
        assigned_tasks_table.rows.clear()
        assigned_tasks_table.rows.extend([
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(group_task[1], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(group_task[3], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(group_task[4], color=ft.colors.BLACK)),
                    ft.DataCell(ft.Text(group_task[5], color=ft.colors.BLACK)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(ft.icons.DELETE, on_click=lambda e,
                                              task_id=group_task[2], group_id=group_task[0]: delete_assignment(group_id, task_id)),
                            ]
                        )
                    ),
                ]
            ) for group_task in fetch_assigned_tasks()
        ])
        page.update()

    # Tabla para mostrar las tareas asignadas a los grupos
    assigned_tasks_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Group", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Assigned Task", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Start Date", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Due Date", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Actions", color=ft.colors.BLACK)),
        ],
        rows=[],
        column_spacing=15,
        data_row_color=ft.colors.WHITE,
        heading_row_color=BG,
        data_row_max_height=80,
        width=700
    )'''

    refresh_assigned_tasks_table()

    return ft.View(
        "/assign_task",
        controls=[
            ft.AppBar(
                title=ft.Text("Assign Task"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/teacher/{teacher_id}")),
                automatically_imply_leading=False
            ),
            ft.Container(
                content=ft.Column(
                    [
                        task_dropdown,
                        group_dropdown,
                        assign_button,
                    ],
                    #spacing=20
                ),
                padding=ft.padding.all(10),
                alignment=ft.alignment.center,
                #margin=5,
            ),
            ft.ListView(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                assigned_task_list,
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
            )
        ],
        bgcolor=FG,
        padding=ft.padding.all(20),
        adaptive=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
