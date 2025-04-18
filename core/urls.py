
from django.urls import path
from .views import home, login_view, cadastro_view, dashboard_view,logout_view, project_create_view, projetos_por_mes_view, projeto_detalhe_view,criar_tarefa_view

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard_view, name="dashboard"),   # <— nome “dashboard”
    path("login/", login_view, name="login"),
    path("cadastro/", cadastro_view, name="cadastro"),
    path("logout/", logout_view, name="logout"),
    path("projects/create/", project_create_view, name="project_create"), 
    path("projetos/<uuid:projeto_id>/", projeto_detalhe_view, name="projeto_detalhe"),
    path("projetos/<uuid:projeto_id>/nova-tarefa/",criar_tarefa_view, name="criar_tarefa"),
    path("api/projetos-mes/", projetos_por_mes_view, name="projetos_por_mes"),
    

]