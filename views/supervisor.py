import flet as ft
from flet_route import Params, Basket
from views.conections import create_connection

FG = '#B7C1F3'
BG = '#8C81BF'

def Supervisor(page: ft.Page, params: Params, basket: Basket):
    #Asignacion de supervisor titulo
    page.title = 'Supervisors Management'
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 550
    admin_id = int(params.get('my_id'))

    def fetch_institutions():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_institution, name FROM institution")
        institutions = cursor.fetchall()
        conn.close()
        return institutions

    def fetch_students(institution_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id_student, s.name, s.last_name, g.name, g.course as group_name
            FROM student s
            JOIN students_group g ON s.id_group = g.id_group
            WHERE g.id_institution = %s
        """, (institution_id,))
        students = cursor.fetchall()
        conn.close()
        return students

    def fetch_supervisors():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_user, name, last_name FROM user WHERE user_type = 'supervisor'")
        supervisors = cursor.fetchall()
        conn.close()
        return supervisors
    
    def fetch_assignments():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id_user, s.name, s.last_name, st.id_student, st.name, st.last_name, sp.relation
            FROM user s
            JOIN supervisor sp ON s.id_user = sp.id_user
            JOIN student st ON sp.id_student = st.id_student
        """)
        assignments = cursor.fetchall()
        conn.close()
        return assignments

    def add_assignment(supervisor_id, student_id, relation):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO supervisor (id_user, id_student, relation) VALUES (%s, %s, %s)", (supervisor_id, student_id, relation,))
        conn.commit()
        conn.close()
        refresh_assignments_list()
        show_confirmation_snackbar("Assignment added successfully.")

    def delete_assignment(supervisor_id, student_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM supervisor WHERE id_user = %s AND id_student = %s", (supervisor_id, student_id,))
        conn.commit()
        conn.close()
        refresh_assignments_list()
        show_confirmation_snackbar("Assignment deleted successfully.")

    def update_assignment(supervisor_id, student_id, relation):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE supervisor SET relation = %s WHERE id_user = %s AND id_student = %s", (relation, supervisor_id, student_id,))
        conn.commit()
        conn.close()
        refresh_assignments_list()
        show_confirmation_snackbar("Assignment updated successfully.")

    def refresh_assignments_list():
        assignments = fetch_assignments()
        assignments_list.controls.clear()
        if assignments:
            for assignment in assignments:
                assignments_list.controls.append(
                    ft.Card(
                        content=ft.Row( #TODO Alinear el texto
                            [   
                                ft.Column(
                                    [   
                                        ft.Text("Supervisor", weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(f"{assignment[1]} {assignment[2]}", size=12),
                                        ft.Text(f"Student ID: {assignment[3]}", weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(f"{assignment[4]} {assignment[5]}", size=12),
                                        ft.Text("Relation", weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(assignment[6], size=12),
                                    ],
                                    width=200,
                                    
                                    tight=True,
                                    spacing=5,
                                    expand=True,
                                    #El contenido de la fila se alinea en el centro
                                    alignment=ft.CrossAxisAlignment.CENTER,
                                ),

                                ft.Row(
                                    [
                                        ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, assignment=assignment: open_edit_assignment_dialog(assignment)),
                                        ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, assignment=assignment: delete_assignment(assignment[0], assignment[3]))
                                    ],
                                    alignment=ft.MainAxisAlignment.END
                                )
                            ],
                            alignment=ft.alignment.center  # Añadido

                        ),
                        margin=3,
                        elevation=2,
                        height=150
                    )
                )
        else:
            show_confirmation_snackbar("No assignments found.")
        page.update()

    def show_confirmation_snackbar(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def open_add_assignment_dialog(e):
        dialog.open = True
        supervisor_dropdown.value = None
        institution_dropdown.value = None
        student_dropdown.options.clear()
        relation_textbox.value = ""
        save_button.disabled = True
        page.update()

    def open_edit_assignment_dialog(assignment):
        edit_supervisor_dropdown.options = [
            ft.dropdown.Option(str(supervisor[0]), f"{supervisor[1]} {supervisor[2]}")
            for supervisor in fetch_supervisors()
        ]
        edit_supervisor_dropdown.value = str(assignment[0])
        edit_dialog.open = True
        edit_institution_dropdown.value = str(fetch_institution_by_student(assignment[3]))
        refresh_edit_student_dropdown(edit_institution_dropdown.value)
        edit_student_dropdown.value = str(assignment[3])
        edit_relation_textbox.value = assignment[6]
        edit_save_button.disabled = False
        page.update()

    def save_new_assignment(e):
        add_assignment(supervisor_dropdown.value, student_dropdown.value, relation_textbox.value)
        dialog.open = False
        page.update()

    def save_edited_assignment(e):
        update_assignment(edit_supervisor_dropdown.value, edit_student_dropdown.value, edit_relation_textbox.value)
        edit_dialog.open = False
        page.update()

    def cancel(e):
        dialog.open = False
        edit_dialog.open = False
        page.update()

    def validate_fields(e):
        supervisor_valid = bool(supervisor_dropdown.value)
        student_valid = bool(student_dropdown.value)
        relation_valid = bool(relation_textbox.value.strip())
        save_button.disabled = not (supervisor_valid and student_valid and relation_valid)
        page.update()

    def validate_edit_fields(e):
        supervisor_valid = bool(edit_supervisor_dropdown.value)
        student_valid = bool(edit_student_dropdown.value)
        relation_valid = bool(edit_relation_textbox.value.strip())
        edit_save_button.disabled = not (supervisor_valid and student_valid and relation_valid)
        page.update()

    def on_institution_change(e):
        selected_institution = institution_dropdown.value
        refresh_supervisor_student_dropdowns(selected_institution)

    def refresh_supervisor_student_dropdowns(institution_id):
        supervisors = fetch_supervisors()
        students = fetch_students(institution_id)

        supervisor_dropdown.options = [
            ft.dropdown.Option(str(supervisor[0]), f"{supervisor[1]} {supervisor[2]}")
            for supervisor in supervisors
        ]
        student_dropdown.options = [
            ft.dropdown.Option(str(student[0]), f"{student[1]} {student[2]} ({student[3]}-{student[4]})")
            for student in students
        ]
        page.update()

    def refresh_edit_student_dropdown(institution_id):
        students = fetch_students(institution_id)
        edit_student_dropdown.options = [
            ft.dropdown.Option(str(student[0]), f"{student[1]} {student[2]} ({student[3]}-{student[4]})")
            for student in students
        ]
        page.update()

    def fetch_institution_by_student(student_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.id_institution
            FROM student s
            JOIN students_group g ON s.id_group = g.id_group
            WHERE s.id_student = %s
        """, (student_id,))
        institution_id = cursor.fetchone()[0]
        conn.close()
        return institution_id

    institutions = fetch_institutions()
    institution_dropdown = ft.Dropdown(
        label="Institution",
        options=[
            ft.dropdown.Option(str(institution[0]), institution[1])
            for institution in institutions
        ],
        on_change=on_institution_change
    )

    supervisors = fetch_supervisors()
    supervisor_dropdown = ft.Dropdown(
        label="Supervisor",
        options=[
            ft.dropdown.Option(str(supervisor[0]), f"{supervisor[1]} {supervisor[2]}")
            for supervisor in supervisors
        ],
        on_change=validate_fields
    )

    student_dropdown = ft.Dropdown(
        label="Student",
        options=[],
        on_change=validate_fields
    )

    relation_textbox = ft.TextField(
        label="Relation",
        on_change=validate_fields
    )

    edit_supervisor_dropdown = ft.Dropdown(
        label="Supervisor",
        options=[],
        on_change=validate_edit_fields
    )

    edit_institution_dropdown = ft.Dropdown(
        label="Institution",
        options=[
            ft.dropdown.Option(str(institution[0]), institution[1])
            for institution in institutions
        ],
        on_change=lambda e: refresh_edit_student_dropdown(edit_institution_dropdown.value)
    )

    edit_student_dropdown = ft.Dropdown(
        label="Student",
        options=[],
        on_change=validate_edit_fields
    )

    edit_relation_textbox = ft.TextField(
        label="Relation",
        on_change=validate_edit_fields
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Add Assignment"),
        content=ft.Column(
            [   
                supervisor_dropdown,
                institution_dropdown,
                student_dropdown,
                relation_textbox
            ],
            tight=True,
            spacing=10
        ),
        actions=[
            ft.ElevatedButton(text="Save", on_click=save_new_assignment),
            ft.OutlinedButton(text="Cancel", on_click=cancel)
        ]
    )

    save_button = dialog.actions[0]

    edit_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Assignment"),
        content=ft.Column(
            [
                edit_supervisor_dropdown,
                edit_institution_dropdown,
                edit_student_dropdown,
                edit_relation_textbox
            ],
            tight=True,
            spacing=10
        ),
        actions=[
            ft.ElevatedButton(text="Save", on_click=save_edited_assignment),
            ft.OutlinedButton(text="Cancel", on_click=cancel)
        ]
    )

    edit_save_button = edit_dialog.actions[0]

    assignments_list = ft.Column(
        controls=[],
        tight=True,
        spacing=10
    )

    add_assignment_button = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=open_add_assignment_dialog)

    refresh_assignments_list()

    return ft.View(
        "/supervisor",
        controls=[
            ft.AppBar(
                title=ft.Text("Supervisors Management"),
                bgcolor=BG,
                leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda e: page.go(f"/admin/{admin_id}")),
            ),
            ft.ListView(
                controls=[
                    assignments_list
                ],
                auto_scroll=True,
                padding=20,
                spacing=10,
                expand=True,
                adaptive=True
            ),
            add_assignment_button,
            dialog,
            edit_dialog
        ],
        bgcolor=FG,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START
    )
