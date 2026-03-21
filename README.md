# wsBackend-Fabrica26.1
# Moneta Backend - Django + REST API

App de gestão de portfólio de investimentos com cotações da BRAPI.

## Instalação rápida

### 1. Clonar e entrar no diretório
```bash
git clone <seu-repo>
cd wsBackend-Fabrica26.1
```

### 2. Criar virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Preparar banco de dados
```bash
cd moneta_backend
python manage.py makemigrations
python manage.py migrate
```

### 5. Criar usuário admin (opcional)
```bash
python manage.py createsuperuser
```

### 6. Rodar servidor
```bash
python manage.py runserver
```

A API estará em: http://localhost:8000

## Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Autenticação**: JWT (djangorestframework-simplejwt)
- **Frontend**: Vanilla JS + HTML/CSS
- **Dados**: SQLite + BRAPI (cotações da B3)
- **CORS**: django-cors-headers

## Estrutura

```
moneta_backend/
├── core/              # Configurações Django
├── moneta/            # App principal (models, views, serializers)
├── templates/         # HTML
├── static/            # JS, CSS
├── utils/
│   └── brapi.py      # Cliente HTTP para BRAPI
└── db.sqlite3        # Banco de dados
```

## Endpoints principais

- `POST /token/` - Login
- `GET/POST /portfolios/` - Listar/criar portfólios
- `DELETE /portfolios/<id>/` - Deletar portfólio
- `GET/POST /portfolios/<id>/assets/` - Gerenciar ativos
- `GET /assets/details/<ticker>/` - Dados do ticker da BRAPI

