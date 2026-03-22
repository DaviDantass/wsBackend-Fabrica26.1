# Moneta Backend API

API REST para gerenciamento de portfólio de investimentos, desenvolvida com **Django**, **DRF**, **JWT** e **BRAPI**. O projeto segue boas práticas de desenvolvimento — estrutura modular, commits semânticos e documentação detalhada — com foco em clareza e manutenibilidade.

**Features:** autenticação JWT, múltiplos portfólios (CRUD), gerenciamento de ativos e sincronização em tempo real com a B3 via BRAPI.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 5.2.12 + Django REST Framework 3.14 |
| Autenticação | simplejwt 5.4 |
| CORS | django-cors-headers 4.3 |
| Dados de mercado | BRAPI (cotações B3) |
| Banco de dados | PostgreSQL 15 |
| Infraestrutura | Docker Compose (Backend + BD) |

---

## Estrutura do projeto
```
moneta_backend/
├── core/              # Config Django (settings, urls, wsgi)
├── moneta/            # App principal
│   ├── models.py      # User, Portfolio, Asset
│   ├── views.py       # REST API + Web views
│   ├── serializers.py # Validações e transformações de dados
│   ├── forms.py       # Formulários web
│   ├── urls.py        # Rotas
│   └── migrations/    # Histórico BD
├── templates/         # HTML (login, dashboard, portfolio)
├── static/            # CSS, JS
├── utils/brapi.py     # Cliente BRAPI com retry automático
├── manage.py
└── requirements.txt
```

---

## Modelos

| Modelo | Campos | Relação |
|--------|--------|---------|
| **User** | username, email*, cpf*, phone | CustomUser |
| **Portfolio** | name, created_at, user | 1-N com User |
| **Asset** | ticker, quantity, purchase_price, company_name, current_price, sector, market_cap, dividend_yield | 1-N com Portfolio |

*Campo único

- Asset sincroniza automaticamente com BRAPI ao ser criado
- Validação de ticker duplicado por portfólio
- Retry automático (3x) com backoff exponencial nas chamadas à BRAPI

---

## Setup

**Pré-requisitos:** Python 3.9+ (recomendado: 3.11.8)
```bash
git clone https://github.com/DaviDantass/wsBackend-Fabrica26.1
cd wsBackend-Fabrica26.1

# Criar e ativar venv
python -m venv venv
# py -3.11 -m venv venv  ← recomendado; adicione como interpreter: Ctrl+Shift+P → "Python: Select Interpreter"
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac

pip install -r requirements.txt

cd moneta_backend
python manage.py migrate
python manage.py createsuperuser  # opcional
python manage.py runserver
```

API disponível em **http://127.0.0.1:8000/**

---

## Docker

⚠️ **IMPORTANTE:** O Docker aqui é **APENAS PARA O BACKEND** (API REST). Ele não contém frontend/interface visual.

**Pré-requisito:** Docker Desktop instalado

### O que o Docker faz:
- ✅ Sobe o **PostgreSQL** (banco de dados)
- ✅ Sobe o **Django** (API backend na porta 8000)
- ❌ **NÃO** inclui frontend/site visual

### Para rodar tudo (Backend + Banco de Dados):
```bash
docker-compose up -d
```

Isso vai:
1. Iniciar PostgreSQL no container `moneta-postgres`
2. Iniciar Django (API) no container `moneta-backend`
3. Aplicar migrations automaticamente
4. Deixar tudo rodando em background

### Acessar:
- **API Backend:** http://localhost:8000
- **Banco de dados:** PostgreSQL na porta 5432 (host: localhost, user: manager, password: manager123)

### Comandos úteis:
```bash
# Ver logs em tempo real
docker-compose logs -f

# Criar superusário (admin)
docker-compose exec django python manage.py createsuperuser

# Parar tudo
docker-compose down

# Parar e remover dados (excluir banco de dados)
docker-compose down -v
```

**O que é persistido:**
- ✅ Dados do PostgreSQL (em volume Docker)
- ✅ Arquivos estáticos da API (CSS/JS do admin Django)

---

## API REST

**Autenticação:** todas as rotas exigem token JWT, exceto `/token/` e `/users/`.

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/token/` | POST | Obter token JWT |
| `/token/refresh/` | POST | Renovar token |
| `/users/` | POST | Registrar usuário |
| `/users/profile/` | GET · PUT | Perfil do usuário |
| `/portfolios/` | GET · POST | Listar/criar portfólios |
| `/portfolios/<id>/` | GET · PUT · DELETE | CRUD portfólio |
| `/portfolios/<id>/assets/` | GET · POST | Listar/criar ativos |
| `/assets/<id>/` | GET · PUT · DELETE | CRUD ativo |
| `/assets/details/<ticker>/` | GET | Dados BRAPI do ticker |
```bash
# Autenticar
curl -X POST http://127.0.0.1:8000/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario","password":"senha"}'
# → {"access":"<token>","refresh":"<token>"}

# Usar token
curl http://127.0.0.1:8000/portfolios/ \
  -H "Authorization: Bearer <token>"
```

**Checklist de produção:**
- `DEBUG=False`
- `SECRET_KEY` via variável de ambiente
- `ALLOWED_HOSTS` específico
- `CORS_ALLOW_ALL_ORIGINS=False`
- HTTPS obrigatório

---

## BRAPI Integration

`utils/brapi.py` implementa retry automático (3×) com backoff exponencial, timeout de 10s, validação de ticker e tratamento de erros HTTP (429, 502, 503).