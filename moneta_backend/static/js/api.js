/**
 * API Client para Moneta Backend
 * Centraliza todas as chamadas à API REST
 */

const API_BASE_URL = '/';
let ACCESS_TOKEN = localStorage.getItem('access_token') || null;

/**
 * Helper para fazer requests com auth
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    if (!ACCESS_TOKEN) {
        throw new Error('Sem token. Faça login novamente.');
    }

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${ACCESS_TOKEN}`,
    };

    const options = {
        method,
        headers,
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            ACCESS_TOKEN = null;
            window.location.href = '/';
            return null;
        }

        if (!response.ok) {
            const errorData = await response.json();
            const errorMessage = errorData.error || errorData.detail || JSON.stringify(errorData);
            throw new Error(errorMessage);
        }

        // 204 No Content - sem corpo de resposta
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * AUTENTICAÇÃO
 */
async function loginUser(username, password) {
    const data = await apiRequest('token/', 'POST', {
        username,
        password,
    });

    if (data.access) {
        ACCESS_TOKEN = data.access;
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        window.location.href = '/dashboard/';
    }
    return data;
}

/**
 * PORTFÓLIOS - RESTful
 */
async function getPortfolios() {
    return await apiRequest('portfolios/');
}

async function createPortfolio(name) {
    return await apiRequest('portfolios/', 'POST', {
        name,
    });
}

async function deletePortfolio(portfolioId) {
    return await apiRequest(`portfolios/${portfolioId}/`, 'DELETE');
}

/**
 * ASSETS
 */
async function getAssets(portfolioId) {
    return await apiRequest(`portfolios/${portfolioId}/assets/`);
}

async function createAsset(portfolioId, ticker, quantity, purchasePrice) {
    return await apiRequest(`portfolios/${portfolioId}/assets/`, 'POST', {
        ticker: ticker.toUpperCase(),
        quantity: parseFloat(quantity),
        purchase_price: parseFloat(purchasePrice),
    });
}

async function deleteAsset(assetId) {
    return await apiRequest(`assets/${assetId}/`, 'DELETE');
}

/**
 * BRAPI - Asset Details (via Backend)
 */
async function getAssetDetails(ticker) {
    try {
        return await apiRequest(`assets/details/${ticker}/`);
    } catch (error) {
        console.error('Erro ao buscar detalhes:', error);
        throw error;
    }
}
