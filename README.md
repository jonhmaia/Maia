# MAIA - Sistema de Produtividade e Gestão de Projetos

MAIA é um sistema completo de produtividade e gerenciamento de projetos com foco em clareza, agilidade e visual moderno. Foi desenvolvido com **Django**, **Supabase**, **Bootstrap 5** e **JavaScript (AJAX + Sortable.js)**.

## 🚀 Funcionalidades Implementadas

### ✅ Autenticação
- Login com email e senha via **Supabase Auth**
- Cadastro de novos usuários com nome
- Validação de sessão com `access_token`
- Logout seguro
- Feedback visual com toast messages

### ✅ Painel do Usuário (Dashboard)
- Navbar e sidebar fixas com dark mode
- KPIs em estilo glassmorphism:
  - Projetos Ativos
  - Tarefas Pendentes
  - Documentos
  - Orçamento Gasto
- Lista de Projetos Recentes em cards interativos
- Criação de projeto via modal
- Navegação para tela de detalhes de projeto

### ✅ Módulo de Tarefas
- Listagem vertical de tarefas com estilo to-do list
- Criação de tarefa via modal com:
  - Título (obrigatório)
  - Prioridade de 1 a 5 com slider colorido e animado
- Drag and drop (reorder) de tarefas no navegador
- Exclusão de tarefas via AJAX sem reload
- Cores dinâmicas com base na prioridade
- Scroll moderno e responsivo para lista de tarefas
- Layout moderno com header fixo para ações

### ✅ Módulo de Orçamento
- Exibição do total gasto com base nos lançamentos
- Lista de lançamentos orçamentários (Receita e Despesa)
- Lançamentos com:
  - Tipo (Receita/Despesa)
  - Categoria
  - Valor
  - Data
  - Descrição
- Criação, edição e exclusão de lançamentos
- Modal de criação visualmente integrado com o design da aplicação

## 📦 Tecnologias Utilizadas

- **Backend:** Django 5.2
- **Frontend:** Bootstrap 5, Toasts, Sortable.js
- **Banco de Dados:** Supabase (PostgreSQL)
- **Autenticação:** Supabase Auth
- **Deploy:** Render (em produção)

## 📁 Estrutura

