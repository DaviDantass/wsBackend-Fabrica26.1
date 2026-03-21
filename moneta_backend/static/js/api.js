/**
 * API Client para Moneta Backend
 * Centraliza todas as chamadas à API REST
 */

const API_BASE_URL = '/';
let ACCESS_TOKEN = localStorage.getItem('access_token') || null;
let LAST_ERROR = null;

console.log('[INIT] API Client carregado. ACCESS_TOKEN:', !!ACCESS_TOKEN);

/**
 * Helper para fazer requests com auth
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    console.log(`[API] Iniciando ${method} ${endpoint}. Token existe?`, !!ACCESS_TOKEN);

    if (!ACCESS_TOKEN) {
        const error = 'Sem token de autenticação. Faça login novamente.';
        console.error('[API]', error);
        LAST_ERROR = error;
        throw new Error(error);
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
        const url = `${API_BASE_URL}${endpoint}`;
        console.log(`[API] ${method} ${url}`, data || '');

        const response = await fetch(url, options);
        console.log(`[API] Resposta recebida: ${response.status} ${response.statusText}`);

        if (response.status === 401) {
            const error = 'Unauthorized - Token expirado';
            console.error('[API]', error);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            ACCESS_TOKEN = null;
            LAST_ERROR = error;
            window.location.href = '/';
            return null;
        }

        let responseData = null;
        try {
            responseData = await response.json();
        } catch (e) {
            console.warn('[API] Resposta não é JSON:', response.status);
        }

        if (!response.ok) {
            const errorMessage = responseData?.error ||
                responseData?.detail ||
                responseData?.message ||
                Object.values(responseData || {}).flat().join(', ') ||
                `HTTP ${response.status}: ${response.statusText}`;

            console.error(`[API] Erro ${response.status}:`, errorMessage);
            LAST_ERROR = errorMessage;
            throw new Error(errorMessage);
        }

        // 204 No Content - sem corpo de resposta
        if (response.status === 204) {
            console.log('[API] OK - 204 No Content');
            return null;
        }

        console.log('[API] OK', responseData);
        LAST_ERROR = null;
        return responseData;
    } catch (error) {
        console.error('[API] Erro na requisição:', error.message);
        LAST_ERROR = error.message;
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

async function updatePortfolioName(portfolioId, newName) {
    return await apiRequest(`portfolios/${portfolioId}/`, 'PATCH', {
        name: newName,
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

/**
 * DEBUG - Para diagnóstico
 */
function debugMoneta() {
    return {
        hasToken: !!ACCESS_TOKEN,
        token: ACCESS_TOKEN ? ACCESS_TOKEN.substring(0, 20) + '...' : null,
        lastError: LAST_ERROR,
        localStorage: {
            access_token: !!localStorage.getItem('access_token'),
            refresh_token: !!localStorage.getItem('refresh_token'),
        },
        timestamp: new Date().toISOString(),
    };
}

console.log('[INIT] Use debugMoneta() para diagnosticar problemas');
