# 📈 Moneta Backend API

API REST para gerenciamento de portfólio de investimentos com **Django 5.2** + **DRF** + **JWT** + **BRAPI**.

🎯 **Features:** Autenticação JWT, múltiplos portfólios(crud), gerencimento de ativos, sincronização em tempo real com BRAPI (B3).

---

## 🛠️ Stack

- **Backend:** Django 5.2.12 + Django REST Framework 3.14
- **Autenticação:** JWT (simplejwt 5.4)
- **CORS:** django-cors-headers 4.3
- **API de dados:** BRAPI (cotações B3)
- **BD:** SQLite (dev), PostgreSQL (prod)

---

## 📁 Estrutura

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

## 📊 Modelos

| Modelo | Campos | Relação |
|--------|--------|---------|
| **User** | username, email*, cpf*, phone | CustomUser |
| **Portfolio** | name, created_at, user | 1-N com User |
| **Asset** | ticker, quantity, purchase_price, company_name, current_price, sector, market_cap, dividend_yield | 1-N com Portfolio |

*Campo único

**Características:**
- Asset sincroniza automaticamente com BRAPI ao criar
- Validação de ticker duplicado por portfólio
- Retry automático (3x) com backoff exponencial para BRAPI

---

## 🚀 Setup Rápido

**Pré-requisitos:** Python 3.9+ (recomendo 3.11.8)

```bash
# Clonar e entrar no diretório
git clone https://github.com/DaviDantass/wsBackend-Fabrica26.1
cd wsBackend-Fabrica26.1

# Criar venv (Python 3.9+)
python -m venv venv
# ou, se tiver Python 3.11 instalado - recomendo, e tambem recomendo adicionar como interpreter depois de criada: ctrl + shift + p: interpreter -> 3.11.8 venv:
py -3.11 -m venv venv

venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Migrações
cd moneta_backend
python manage.py migrate

# Admin (opcional)
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

✅ API em: **http://127.0.0.1:8000/**

---

## 📡 API REST

**Autenticação:** Todas as rotas requerem token JWT (exceto `/token/` e `/register/`)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/token/` | POST | Obter token JWT |
| `/token/refresh/` | POST | Renovar token |
| `/users/` | POST | Registrar novo usuário |
| `/users/profile/` | GET/PUT | Perfil do usuário |
| `/portfolios/` | GET/POST | Listar/criar portfólios |
| `/portfolios/<id>/` | GET/PUT/DELETE | CRUD portfólio |
| `/portfolios/<id>/assets/` | GET/POST | Listar/criar ativos |
| `/assets/<id>/` | GET/PUT/DELETE | CRUD ativo |
| `/assets/details/<ticker>/` | GET | Dados BRAPI do ticker |

**Exemplo de requisição:**
```bash
# Login
curl -X POST http://127.0.0.1:8000/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario","password":"senha"}'

# Resultado: {"access":"token_jwt...","refresh":"token..."}

# Usar token
curl -X GET http://127.0.0.1:8000/portfolios/ \
  -H "Authorization: Bearer token_jwt..."
```

**Produção:**
- ❌ DEBUG=False
- ❌ Guardar SECRET_KEY fechada (use env vars)
- ❌ ALLOWED_HOSTS específico
- ❌ CORS_ALLOW_ALL_ORIGINS=False
- ❌ Database: PostgreSQL
- ✅ HTTPS obrigatório

---

## 📚 BRAPI Integration (gratuita)

`utils/brapi.py` implementa:
- ✅ Retry automático (3x) com backoff exponencial
- ✅ Timeout 10s
- ✅ Validação de ticker
- ✅ Tratamento de erros (429, 502, 503)

