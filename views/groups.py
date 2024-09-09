import flet as ft
from flet_route import Params, Basket
import sqlite3 as sql
import re
from .conections import create_connection

FG = '#B7C1F3'
BG = '#8C81BF'

def Groups(page: ft.Page, params: Params, basket: Basket):
    page.title = 'Groups Management'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 550
    admin_id = int(params.get('my_id'))

    def fetch_groups(institution_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id_group, g.name, g.course, g.id_institution, 
                IFNULL(CONCAT(u.name, ' ', u.last_name), 'sin asignar') as professor
            FROM students_group g
            LEFT JOIN teacher t ON g.id_teacher = t.id_teacher
            LEFT JOIN user u ON t.id_teacher = u.id_user
            WHERE g.id_institution = %s
        """, (institution_id,))
        groups = cursor.fetchall()
        conn.close()
        return groups

    def fetch_institutions(admin_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_institution, name FROM institution WHERE id_administrator = %s", (admin_id,))
        institutions = cursor.fetchall()
        conn.close()
        return institutions

    def fetch_teachers():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_user, CONCAT(u.name, ' ', u.last_name) AS full_name 
            FROM user u 
            JOIN teacher t ON u.id_user = t.id_teacher
        """)
        teachers = cursor.fetchall()
        conn.close()
        return teachers

    def add_group(name, course, institution_id, teacher_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students_group (name, course, id_institution, id_teacher) VALUES (%s, %s, %s, %s)", (name, course, institution_id, teacher_id,))
        conn.commit()
        conn.close()
        refresh_groups_table()
        show_confirmation_snackbar("Group added successfully.")

    def edit_group(group_id, name, course, institution_id, teacher_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students_group SET name = %s, course = %s, id_institution = %s, id_teacher = %s WHERE id_group = %s", (name, course, institution_id, teacher_id, group_id,))
        conn.commit()
        conn.close()
        refresh_groups_table()
        show_confirmation_snackbar("Group updated successfully.")

    def delete_group(group_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students_group WHERE id_group = %s", (group_id,))
        conn.commit()
        conn.close()
        refresh_groups_table()
        show_confirmation_snackbar("Group deleted successfully.")

    def refresh_groups_table():
        if institution_dropdown.value is None:
            return
            
        selected_institution_id = int(institution_dropdown.value)
        groups = fetch_groups(selected_institution_id)
        groups_table.rows.clear()
        if groups:
            groups_table.rows.extend([
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(group[0]), color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(str(group[1]), color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(group[2], color=ft.colors.BLACK)),
                        ft.DataCell(ft.Text(group[4], color=ft.colors.BLACK)),  # Profesor
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, group=group: open_edit_group_dialog(group)),
                                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, group=group: delete_group(group[0]))
                                ]
                            )
                        )
                    ]
                )
                for group in groups
            ])
        else:
            show_confirmation_snackbar("No groups registered")

        page.update()

    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def open_add_group_dialog(e):
        dialog.open = True
        dialog_title.value = "Add Group"
        nameG_input.value = ""
        course_input.value = ""
        teacher_dropdown.value = None
        save_button.on_click = save_new_group
        save_button.disabled = True
        cancel_button.on_click = cancel
        page.update()

    def save_new_group(e):
        add_group(nameG_input.value, course_input.value, institution_dropdown.value, teacher_dropdown.value)
        dialog.open = False
        page.update()

    def cancel(e):
        dialog.open = False
        page.update()

    def open_edit_group_dialog(group):
        dialog.open = True
        dialog_title.value = "Edit Group"
        nameG_input.value = group[1]
        course_input.value = group[2]
        teacher_dropdown.value = group[4]
        save_button.on_click = lambda e: save_edited_group(group[0])
        save_button.disabled = False
        cancel_button.on_click = cancel
        page.update()

    def save_edited_group(group_id):
        edit_group(group_id, nameG_input.value, course_input.value, institution_dropdown.value, teacher_dropdown.value)
        dialog.open = False
        page.update()

    def validate_fields(e):
        nameG_valid = bool(nameG_input.value.strip())
        course_valid = bool(course_input.value.strip())
        teacher_id_valid = bool(teacher_dropdown.value)
        #Se valida que en grupo se escriba "GR#numero de grupo"
        if not re.match(r"GR\d+", nameG_input.value.strip()):
            nameG_input.error_text = "Invalid group name format. Must be: GR#numero de grupo"
        else:
            nameG_input.error_text = None

        if not nameG_valid:
            nameG_input.error_text = "Name cannot be empty."
        else:
            nameG_input.error_text = None

        if not course_valid:
            course_input.error_text = "Course cannot be empty."
        else:
            course_input.error_text = None

        if not teacher_id_valid:
            teacher_dropdown.error_text = "Please select a teacher."
        else:
            teacher_dropdown.error_text = None

        save_button.disabled = not (nameG_valid and course_valid and teacher_id_valid)
        page.update()

    teachers = fetch_teachers()
    teacher_dropdown = ft.Dropdown(
        label="Teacher",
        options=[
            ft.dropdown.Option(str(teacher[0]), teacher[1])
            for teacher in teachers
        ],
        on_change=validate_fields
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(),
        content=ft.Column(
            [
                ft.TextField(label="Grupo(GR)", on_change=validate_fields),
                ft.TextField(label="Course", on_change=validate_fields),
                teacher_dropdown
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
    nameG_input = dialog.content.controls[0]
    course_input = dialog.content.controls[1]
    save_button = dialog.actions[0]
    cancel_button = dialog.actions[1]

    groups_table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Grupo", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Course", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Professor", color=ft.colors.BLACK)),
            ft.DataColumn(label=ft.Text("Actions", color=ft.colors.BLACK))
        ],
        rows=[],
        column_spacing=15,
        data_row_color=ft.colors.WHITE,
        heading_row_color=BG
    )

    institutions = fetch_institutions(admin_id)
    institution_dropdown = ft.Dropdown(
        label="Institution",
        options=[
            ft.dropdown.Option(str(inst[0]), inst[1])
            for inst in institutions
        ],
        value=None,
        on_change=lambda e: refresh_groups_table()
    )

    add_group_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_group_dialog)

    def load_initial_data():
        institutions = fetch_institutions(admin_id)
        institution_dropdown.options = [
            ft.dropdown.Option(str(inst[0]), inst[1])
            for inst in institutions
        ]
        institution_dropdown.value = None
        refresh_groups_table()

    page.on_view_load = load_initial_data

    return ft.View(
        "/groups",
        controls=[
            ft.AppBar(
                title=ft.Text("Groups Management"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/admin/{admin_id}")),
            ),
            ft.Row(
                controls=[
                    institution_dropdown,
                    ft.IconButton(icon=ft.icons.REFRESH, on_click=lambda e: refresh_groups_table())
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.ListView(
                controls=[
                    groups_table
                ],
                auto_scroll=True,
                padding=20,
                spacing=10,
                expand=True,
                adaptive=True
            ),
            add_group_button,
            dialog
        ],
        bgcolor=FG,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START
    )
