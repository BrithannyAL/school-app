import flet as ft
from flet_route import Routing, path
from views.login import Login
from views.regis_institucion import Regis_institucion
from views.admin import Admin
from views.supervisor import Supervisor
from views.teacher import Teacher
from views.users import Users
from views.groups import Groups
from views.students import Students
from views.institutions import Institutions
from views.panel_supervisor import Panel_supervisor
from views.tasks_supervisor import Tasks_supervisor
from views.tasks import Task
from views.assign_task import Assign_task
from views.chat_supervisor import Chat_supervisor
from views.chat_view_sup import Chat_view_sup 
from views.teacher_chat import Chat_teacher
from views.chat_view_teach import Chat_view_chat

def main(page:ft.Page):
    
    #Rutas de la app
    app_routes = [
        path(url = "/", clear =True, view=Login),
        path(url = "/registerIns/:my_id",clear = False, view=Regis_institucion),
        path(url = "/admin/:my_id", clear =False, view=Admin),
        path(url = "/supervisor/:my_id", clear =False, view=Supervisor),
        path(url = "/teacher/:my_id", clear =False, view=Teacher),
        path(url = "/users/:my_id", clear =False, view=Users),
        path(url = "/groups/:my_id", clear =False, view=Groups),    
        path(url = "/assign_task/:my_id", clear =False, view=Assign_task), 
        path(url = "/students/:my_id", clear =False, view=Students),
        path(url = "/tasks/:my_id", clear =False, view=Task),
        path(url = "/institutions/:my_id", clear =False, view=Institutions),      
        path(url = "/tasks/:my_id", clear =False, view=Task),       
        path(url = "/panel_supervisor/:my_id", clear =False, view=Panel_supervisor),
        path(url = "/tasks_supervisor/:my_id", clear =False, view=Tasks_supervisor),
        path(url = "/chat_supervisor/:my_id", clear =False, view=Chat_supervisor),
        path(url = "/chat_supervisor/chat/:my_id/:teacher_id", clear =False, view=Chat_view_sup),
        path(url = "/teacher_chat/:my_id", clear =False, view=Chat_teacher),
        path(url = "/teacher_chat/chat_view/:my_id/:supervisor_id", clear =False, view=Chat_view_chat),
    ]

    #Se crea una instancia de la clase Routing
    Routing(page=page, app_routes=app_routes) 
    
    #Se muestra la vista de la ruta actual
    page.go(page.route)


ft.app(target=main, assets_dir="assets")