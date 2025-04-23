from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from functools import wraps
from django.conf import settings
from supabase import create_client, Client
from postgrest.exceptions import APIError
from .supabase_client import supabase
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Inicializa o cliente Supabase (caso necessário novamente)
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Views públicas
def home(request):
    return render(request, "core/home.html")

def projetos(request):
    return render(request, "core/projetos.html")

def entrar(request):
    return render(request, "core/entrar.html")

# Middleware de login
def login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get("access_token"):
            messages.error(request, "Você precisa fazer login para acessar essa página.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return _wrapped

# Logout
def logout_view(request):
    try:
        request.session.flush()
        messages.info(request, "Você foi desconectado com sucesso.")
    except Exception:
        messages.warning(request, "Ocorreu um erro ao tentar sair.")
    return redirect("login")

# Home autenticada
@login_required
def home_view(request):
    return render(request, "core/home.html")

# Dashboard
@login_required
def dashboard_view(request):
    return render(request, "core/dashboard.html")

# Login
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            resp = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not resp.user or not resp.session:
                messages.error(request, "Credenciais inválidas.")
                return render(request, "core/login.html")

            request.session["user_id"] = resp.user.id
            request.session["access_token"] = resp.session.access_token
            messages.success(request, "Logado com sucesso!")
            return redirect("dashboard")

        except Exception as e:
            messages.error(request, f"Erro ao fazer login: {e}")
            return render(request, "core/login.html")

    return render(request, "core/login.html")

# Cadastro
def cadastro_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")
        try:
            result = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "data": {
                    "name": name
                }
            })
            print("SIGN UP RESULT:", result)
            if result.user:
                messages.success(request, "Cadastro realizado! Você já pode fazer login.")
                return redirect("login")
            else:
                messages.error(request, "Erro ao criar conta.")
        except Exception as e:
            print("Erro no cadastro:", e)
            messages.error(request, f"Erro no cadastro: {e}")
        return redirect("cadastro")
    return render(request, "core/cadastro.html")

# Criação de projetos
@login_required
def project_create_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        usuario_id = request.session.get("user_id")

        if not nome or not descricao:
            messages.error(request, "Nome e descrição são obrigatórios.")
            return redirect("dashboard")

        payload = {
            "nome": nome,
            "descricao": descricao,
            "usuario_id": usuario_id,
        }

        try:
            result = supabase.table("projetos").insert(payload).execute()
            messages.success(request, "Projeto criado com sucesso.")
        except Exception as e:
            print("Erro ao criar projeto:", e)
            messages.error(request, f"Erro ao criar projeto: {e}")

    return redirect("dashboard")
from datetime import datetime
from django.utils.dateparse import parse_datetime

@login_required
def dashboard_view(request):
    user_id = request.session.get("user_id")
    response = supabase.table("projetos").select("*").eq("usuario_id", user_id).order("criado_em", desc=True).execute()
    projetos = response.data if response.data else []

    for projeto in projetos:
        if "criado_em" in projeto:
            projeto["criado_em"] = parse_datetime(projeto["criado_em"])

    return render(request, "core/dashboard.html", {"projetos": projetos})

from django.http import JsonResponse
from datetime import datetime
from collections import defaultdict
from core.supabase_client import supabase

@login_required
def projetos_por_mes_view(request):
    user_id = request.session.get("user_id")
    response = supabase.table("projetos").select("*").eq("usuario_id", user_id).execute()
    projetos = response.data

    contagem_por_mes = defaultdict(int)
    for projeto in projetos:
        criado_em = projeto.get("criado_em")
        if criado_em:
            dt = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
            mes_formatado = dt.strftime("%b/%Y")  # Ex: Abr/2025
            contagem_por_mes[mes_formatado] += 1

    # Ordena por data
    meses_ordenados = sorted(contagem_por_mes.items(), key=lambda x: datetime.strptime(x[0], "%b/%Y"))

    labels = [m[0] for m in meses_ordenados]
    valores = [m[1] for m in meses_ordenados]
    return JsonResponse({"labels": labels, "valores": valores})



@login_required
def projeto_detalhe_view(request, projeto_id):
    try:
        # Busca o projeto
        projeto_resp = supabase.table("projetos").select("*").eq("id", str(projeto_id)).single().execute()
        projeto = projeto_resp.data

        # Busca tarefas associadas
        tarefas_resp = supabase.table("tarefas").select("*").eq("projeto_id", str(projeto_id)).execute()
        tarefas = tarefas_resp.data if tarefas_resp.data else []

        return render(request, "core/projeto_detalhe.html", {
            "projeto": projeto,
            "tarefas": tarefas
        })

    except Exception as e:
        messages.error(request, f"Erro ao carregar projeto: {e}")
        return redirect("dashboard")
@login_required
def criar_tarefa_view(request, projeto_id):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
       
      
        prioridade = request.POST.get("prioridade")

        # Verificação básica
        if not titulo or not prioridade:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return redirect("projeto_detalhe", projeto_id=projeto_id)

        try:
            payload = {
                "projeto_id": str(projeto_id),
                "titulo": titulo,
              
                "prioridade": int(prioridade) if prioridade else 1,
            }
            supabase.table("tarefas").insert(payload).execute()
            messages.success(request, "Tarefa criada com sucesso!")
        except Exception as e:
            print("Erro ao criar tarefa:", e)
            messages.error(request, "Erro ao criar tarefa.")

    return redirect("projeto_detalhe", projeto_id=projeto_id)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
@login_required
def deletar_tarefa(request, projeto_id, tarefa_id):
    if request.method == "POST":
        try:
            supabase.table("tarefas").delete().eq("id", str(tarefa_id)).execute()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
        
    return JsonResponse({"success": False, "error": "Método inválido"})



from django.shortcuts import redirect
from django.contrib import messages
from .supabase_client import supabase
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from datetime import datetime

@csrf_exempt
@login_required
def criar_lancamento_orcamento_view(request, projeto_id):
    if request.method == "POST":
        tipo = request.POST.get("tipo")  # entrada ou saída
        categoria = request.POST.get("categoria")
        valor = request.POST.get("valor")
        data = request.POST.get("data")
        descricao = request.POST.get("descricao")

        if not tipo or not valor or not data:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return redirect("projeto_detalhe", projeto_id=projeto_id)

        try:
            payload = {
                "projeto_id": projeto_id,
                "tipo": tipo,
                "categoria": categoria,
                "valor": float(valor),
                "data": parse_date(data),
                "descricao": descricao
            }
            supabase.table("lancamentos_orcamento").insert(payload).execute()
            messages.success(request, "Lançamento criado com sucesso!")
        except Exception as e:
            print("Erro ao criar lançamento:", e)
            messages.error(request, "Erro ao criar lançamento.")

    return redirect("projeto_detalhe", projeto_id=projeto_id)



@login_required
def editar_lancamento_view(request, projeto_id, lancamento_id):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        categoria = request.POST.get("categoria")
        valor = request.POST.get("valor")
        data = request.POST.get("data")
        descricao = request.POST.get("descricao")

        try:
            payload = {
                "tipo": tipo,
                "categoria": categoria,
                "valor": float(valor),
                "data": data,
                "descricao": descricao,
            }
            supabase.table("lancamentos_orcamento").update(payload).eq("id", str(lancamento_id)).execute()
            messages.success(request, "Lançamento atualizado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao editar lançamento: {e}")

    return redirect("projeto_detalhe", projeto_id=projeto_id)

@csrf_exempt
@login_required
def deletar_lancamento_view(request, projeto_id, lancamento_id):
    if request.method == "POST":
        try:
            supabase.table("lancamentos_orcamento").delete().eq("id", str(lancamento_id)).execute()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Método inválido"})
