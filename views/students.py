import flet as ft
from flet_route import Params, Basket
import sqlite3 as sql
import mysql.connector
from .conections import create_connection

FG = '#B7C1F3'
BG = '#8C81BF'

def Students(page: ft.Page, params: Params, basket: Basket):
    page.title = 'Students Management'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 550

    # Obteniendo el ID del administrador desde los parámetros o la cesta
    # Extraer el valor de my_id
    admin_id = int(params.get('my_id'))

    # Función para obtener las instituciones asignadas al administrador
    def fetch_institutions_for_admin(admin_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_institution, name 
            FROM institution 
            WHERE id_administrator = %s
        """, (admin_id,))
        institutions = cursor.fetchall()
        conn.close()
        return institutions

    # Función para obtener los grupos de una institución
    def fetch_groups(institution_id):   
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_group, name, course 
            FROM students_group
            WHERE id_institution = %s
        """, (institution_id,))
        groups = cursor.fetchall()
        conn.close()
        return groups

    # Función para obtener los estudiantes de un grupo
    def fetch_students(group_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_student, name, last_name 
            FROM student 
            WHERE id_group = %s
        """, (group_id,))
        students = cursor.fetchall()
        print(students)
        conn.close()
        return students

    # Función para añadir un nuevo estudiante
    def add_student(name, last_name, group_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO student (name, last_name, id_group) VALUES (%s, %s, %s)", (name, last_name, group_id))
        conn.commit()
        conn.close()
        refresh_students_table()
        show_confirmation_snackbar("Student added successfully.")

    # Función para editar un estudiante existente
    def edit_student(student_id, name, last_name, group_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE student SET name = %s, last_name = %s, id_group = %s WHERE id_student = %s", (name, last_name, group_id, student_id))
        conn.commit()
        conn.close()
        refresh_students_table()
        show_confirmation_snackbar("Student updated successfully.")

    # Función para eliminar un estudiante
    def delete_student(student_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student WHERE id_student = %s", (student_id,))
        conn.commit()
        conn.close()
        refresh_students_table()
        show_confirmation_snackbar("Student deleted successfully.")

    # Refrescar la tabla de estudiantes
    def refresh_students_table():
        if group_dropdown.value is None:
            return
        selected_group_id = int(group_dropdown.value)
        students = fetch_students(selected_group_id)
        print("estoy dentro del refresh")
        students_table.rows.clear()
        if students:
            students_table.rows.extend([
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(student[0]), color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(student[1], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(student[2], color=ft.colors.BLACK)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, student=student: open_edit_student_dialog(student)),
                                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, student=student: delete_student(student[0]))
                                ]
                            )
                        )
                    ]
                )
                for student in students
            ])
        else:
            show_confirmation_snackbar("No students were found associated with this course")
        page.update()

    # Mostrar snackbar de confirmación
    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    # Abrir el dialogo para añadir un nuevo estudiante
    def open_add_student_dialog(e):
        dialog.open = True
        dialog_title.value = "Add Student"
        student_name_input.value = ""
        student_last_name_input.value = ""
        group_id_input.value = group_dropdown.value
        save_button.on_click = save_new_student
        save_button.disabled = True  # Inicialmente deshabilitado
        cancel_button.on_click = cancel
        page.update()

    # Guardar el nuevo estudiante
    def save_new_student(e):
        add_student(student_name_input.value, student_last_name_input.value, group_id_input.value)
        dialog.open = False
        page.update()

    # Cancelar
    def cancel(e):
        dialog.open = False
        page.update()

    # Abrir el dialogo para editar un estudiante
    def open_edit_student_dialog(student):
        dialog.open = True
        dialog_title.value = "Edit Student"
        student_name_input.value = student[1]
        student_last_name_input.value = student[2]
        group_id_input.value = group_dropdown.value
        save_button.on_click = lambda e: save_edited_student(student[0])
        save_button.disabled = False  # Habilitado cuando editamos un estudiante existente
        cancel_button.on_click = cancel
        page.update()

    # Guardar los cambios del estudiante editado
    def save_edited_student(student_id):
        edit_student(student_id, student_name_input.value, student_last_name_input.value, group_id_input.value)
        dialog.open = False
        page.update()

    # Validar campos
    def validate_fields(e):
        name_valid = bool(student_name_input.value.strip())
        last_name_valid = bool(student_last_name_input.value.strip())
        group_id_valid = bool(group_id_input.value.strip().isdigit())

        if not name_valid:
            student_name_input.error_text = "Name cannot be empty."
        else:
            student_name_input.error_text = None

        if not last_name_valid:
            student_last_name_input.error_text = "Last Name cannot be empty."
        else:
            student_last_name_input.error_text = None

        if not group_id_valid:
            group_id_input.error_text = "Group ID must be a number."
        else:
            group_id_input.error_text = None

        save_button.disabled = not (name_valid and last_name_valid and group_id_valid)
        page.update()

    # Componentes del dialogo de estudiante
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(),
        content=ft.Column(
            [
                ft.TextField(label="Name", on_change=validate_fields),
                ft.TextField(label="Last Name", on_change=validate_fields),
                ft.TextField(label="Course ID", on_change=validate_fields)
            ],
            tight=True,
            spacing=10
        ),
        actions=[
            ft.ElevatedButton(text="Save", on_click=None),
            ft.OutlinedButton(text="Cancel", on_click=None)
        ]
    )
    dialog_title = dialog.title
    student_name_input = dialog.content.controls[0]
    student_last_name_input = dialog.content.controls[1]
    group_id_input = dialog.content.controls[2]
    save_button = dialog.actions[0]
    cancel_button = dialog.actions[1]

    # Tabla de estudiantes
    students_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID Student", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Name", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Last Name", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Actions", color=ft.colors.BLACK))
        ],
        rows=[],
        column_spacing=15,
        data_row_color=ft.colors.WHITE,
        heading_row_color=BG
    )

    # Dropdown de instituciones
    institutions = fetch_institutions_for_admin(admin_id)
    institution_dropdown = ft.Dropdown(
        label="Institution",
        options=[
            ft.dropdown.Option(str(inst[0]), inst[1])
            for inst in institutions
        ],
        value=str(institutions[0][0]) if institutions else None,
        on_change=lambda e: refresh_groups_dropdown()
    )

    # Dropdown de grupos
    group_dropdown = ft.Dropdown(
        label="Group",
        options=[],
        on_change=lambda e: refresh_students_table()
    )

    # Refrescar dropdown de grupos
    def refresh_groups_dropdown():
        if institution_dropdown.value is None:
            print("estoy dentro del acurlizar grupos")
            return
        selected_institution_id = int(institution_dropdown.value)
        groups = fetch_groups(selected_institution_id)
        group_dropdown.options.clear()
        #Se verifica que la lista no este vacia
        if groups:  
            group_dropdown.options.extend([
                ft.dropdown.Option(str(group[0]), f"{group[1]} - {group[2]}")
                for group in groups
            ])
            group_dropdown.value = str(groups[0][0]) if groups else None
            refresh_students_table()
        else:
            show_confirmation_snackbar("No groups were found associated with this institution")
        page.update()

    # Botón para añadir un nuevo estudiante
    add_student_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_student_dialog)

    # Refrescar la tabla inicial
    refresh_groups_dropdown()

    # Vista de la página de estudiantes
    return ft.View(
        "/students",
        controls=[
            ft.AppBar(
                title=ft.Text("Students Management"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/admin/{admin_id}")),
            ),
            ft.Row(
                controls=[
                    institution_dropdown,
                    group_dropdown,
                    ft.IconButton(icon=ft.icons.SEARCH, on_click=lambda e: refresh_students_table())
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.ListView(
                controls=[
                    students_table
                ],
                auto_scroll=True,
                padding=20,
                spacing=10,
                expand=True,
                adaptive=True
            ),
            add_student_button,
            dialog
        ],
        bgcolor=FG,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START
    )
