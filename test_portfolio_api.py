#!/usr/bin/env python
"""
Script de teste para a API de Portfólios
Testa CREATE, READ, UPDATE, DELETE
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Credenciais de teste
USERNAME = "testuser"
PASSWORD = "testpass123"
EMAIL = "test@example.com"
CPF = "123.456.789-00"

def log(message, status="INFO"):
    print(f"\n[{status}] {message}")

def test_create_user():
    """Criar usuário de teste"""
    log("Criando usuário de teste...", "START")
    
    data = {
        "username": USERNAME,
        "email": EMAIL,
        "cpf": CPF,
        "password": PASSWORD,
        "password2": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=data)
    
    if response.status_code in (201, 400):  # 201 criado, 400 já existe
        log(f"Usuário pronto: {USERNAME}", "OK")
        return True
    else:
        log(f"Erro ao criar usuário: {response.status_code} - {response.text}", "ERROR")
        return False

def test_login():
    """Login e obter token JWT"""
    log("Fazendo login...", "START")
    
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/token/", json=data)
    
    if response.status_code == 200:
        token = response.json().get('access')
        log(f"Token obtido: {token[:20]}...", "OK")
        return token
    else:
        log(f"Erro ao fazer login: {response.status_code} - {response.text}", "ERROR")
        return None

def test_create_portfolio(token):
    """Criar um portfólio"""
    log("Criando portfólio...", "START")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"name": "Teste Portfolio"}
    
    response = requests.post(f"{BASE_URL}/portfolios/", json=data, headers=headers)
    
    if response.status_code == 201:
        portfolio = response.json()
        log(f"Portfólio criado! ID: {portfolio['id']}, Nome: {portfolio['name']}", "OK")
        return portfolio['id']
    else:
        log(f"Erro ao criar portfólio: {response.status_code} - {response.text}", "ERROR")
        return None

def test_list_portfolios(token):
    """Listar portfólios"""
    log("Listando portfólios...", "START")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/portfolios/", headers=headers)
    
    if response.status_code == 200:
        portfolios = response.json()
        log(f"Total de portfólios: {len(portfolios)}", "OK")
        for p in portfolios:
            print(f"  - ID: {p['id']}, Nome: {p['name']}")
        return portfolios
    else:
        log(f"Erro ao listar portfólios: {response.status_code} - {response.text}", "ERROR")
        return None

def test_get_portfolio(token, portfolio_id):
    """Obter detalhes de um portfólio"""
    log(f"Obtendo portfólio {portfolio_id}...", "START")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/portfolios/{portfolio_id}/", headers=headers)
    
    if response.status_code == 200:
        portfolio = response.json()
        log(f"Portfólio encontrado: {portfolio['name']}", "OK")
        return portfolio
    else:
        log(f"Erro ao obter portfólio: {response.status_code} - {response.text}", "ERROR")
        return None

def test_update_portfolio(token, portfolio_id):
    """Atualizar nome do portfólio"""
    log(f"Atualizando portfólio {portfolio_id}...", "START")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"name": "Portfólio Atualizado"}
    
    response = requests.put(f"{BASE_URL}/portfolios/{portfolio_id}/", json=data, headers=headers)
    
    if response.status_code == 200:
        portfolio = response.json()
        log(f"Portfólio atualizado! Novo nome: {portfolio['name']}", "OK")
        return True
    else:
        log(f"Erro ao atualizar portfólio: {response.status_code} - {response.text}", "ERROR")
        return False

def test_delete_portfolio(token, portfolio_id):
    """Deletar um portfólio"""
    log(f"Deletando portfólio {portfolio_id}...", "START")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(f"{BASE_URL}/portfolios/{portfolio_id}/", headers=headers)
    
    if response.status_code == 204:
        log(f"Portfólio deletado com sucesso!", "OK")
        return True
    else:
        log(f"Erro ao deletar portfólio: {response.status_code} - {response.text}", "ERROR")
        return False

def main():
    print("=" * 60)
    print("TESTE DE API - PORTFÓLIOS")
    print("=" * 60)
    
    # Criar usuário
    if not test_create_user():
        return
    
    # Login
    token = test_login()
    if not token:
        return
    
    # CRUD
    portfolio_id = test_create_portfolio(token)
    
    if portfolio_id:
        test_list_portfolios(token)
        test_get_portfolio(token, portfolio_id)
        test_update_portfolio(token, portfolio_id)
        test_delete_portfolio(token, portfolio_id)
    
    print("\n" + "=" * 60)
    print("FIM DO TESTE")
    print("=" * 60)

if __name__ == "__main__":
    main()
