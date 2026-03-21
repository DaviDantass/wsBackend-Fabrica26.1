/**
 * portfolio_detail.js — Moneta
 */

let currentPortfolio = null;
let currentAssets = [];
let tokenCheckAttempted = false;
let portfolioId = null; // Definir globalmente

document.addEventListener('DOMContentLoaded', () => {
    // Obter ID do portfólio da URL
    portfolioId = new URLSearchParams(window.location.search).get('id');
    if (!portfolioId) {
        showNotification('Portfólio não encontrado', 'error');
        setTimeout(() => window.location.href = '/dashboard/', 2000);
        return;
    }
    initPortfolioDetail();
});

async function initPortfolioDetail() {
    try {
        // Se não tem token e ainda não tentou buscar, buscar da API
        if (!ACCESS_TOKEN && !tokenCheckAttempted) {
            tokenCheckAttempted = true;
            const success = await fetchTokenFromSession();
            if (!success) {
                showNotification('Erro: Sem autenticação. Faça login novamente.', 'error');
                setTimeout(() => window.location.href = '/', 2000);
                return;
            }
        }

        // Se não tem token agora, redirecionar (não ficar em loop)
        if (!ACCESS_TOKEN) {
            showNotification('Erro: Sem autenticação. Faça login novamente.', 'error');
            setTimeout(() => window.location.href = '/', 2000);
            return;
        }

        await loadPortfolioDetail();
    } catch (err) {
        showNotification('Erro ao inicializar portfólio', 'error');
        console.error(err);
    }
}

async function fetchTokenFromSession() {
    try {
        const response = await fetch('/auth/session-token/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Inclui cookies de sessão
        });

        if (response.ok) {
            const data = await response.json();
            if (data.access) {
                ACCESS_TOKEN = data.access;
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                return true;
            }
        }
        return false;
    } catch (err) {
        console.error('Erro ao buscar token:', err);
        return false;
    }
}

async function loadPortfolioDetail() {
    try {
        console.log('[Portfolio] Carregando portfolios...');
        const portfolios = await getPortfolios();
        console.log('[Portfolio] Portfolios recebidos:', portfolios);

        currentPortfolio = portfolios.find(p => p.id == portfolioId);
        console.log('[Portfolio] Portfolio encontrado:', currentPortfolio);

        if (!currentPortfolio) {
            showNotification('Portfólio não encontrado', 'error');
            setTimeout(() => window.location.href = '/dashboard/', 2000);
            return;
        }

        document.getElementById('portfolio-name').textContent = currentPortfolio.name;

        // Formatamos a data corretamente
        const dataFormatada = new Date(currentPortfolio.created_at).toLocaleDateString('pt-BR');
        document.getElementById('portfolio-created').textContent = `Criado em: ${dataFormatada}`;
        console.log('[Portfolio] Data:', currentPortfolio.created_at, '→', dataFormatada);

        await loadAssets();
    } catch (err) {
        console.error('[Portfolio] Erro ao carregar:', err);
        showNotification('Erro ao carregar portfólio: ' + err.message, 'error');
    }
}

async function loadAssets() {
    try {
        currentAssets = await getAssets(portfolioId);
        renderAssets();
    } catch (err) {
        showNotification('Erro ao carregar assets', 'error');
        console.error(err);
    }
}

function renderAssets() {
    const tbody = document.getElementById('assets-tbody');
    document.getElementById('asset-count').textContent = currentAssets.length;

    if (currentAssets.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align:center;padding:48px;color:#c0c0c0;">
                    Nenhum asset adicionado ainda
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = currentAssets.map(asset => {
        const priceChange = asset.price_change_percent ? parseFloat(asset.price_change_percent) : 0;
        const changeColor = priceChange >= 0 ? '#2fe878' : '#ff3c3c';
        return `
        <tr>
            <td><span class="ticker-badge ticker-clickable" onclick="openAssetDetailsModal('${asset.ticker}')" style="cursor:pointer;">${asset.ticker}</span></td>
            <td>${asset.company_name || '-'}</td>
            <td>${asset.sector || '-'}</td>
            <td>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span>R$ ${asset.current_price ? parseFloat(asset.current_price).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '-'}</span>
                    <span style="color:${changeColor};font-size:.85rem;font-weight:600;">${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)}%</span>
                </div>
            </td>
            <td>${parseFloat(asset.quantity).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
            <td>R$ ${parseFloat(asset.purchase_price).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
            <td>
                <button class="btn-delete" onclick="confirmDeleteAsset(${asset.id}, '${asset.ticker}')">
                    Excluir
                </button>
            </td>
        </tr>
    `;
    }).join('');
}

function openAddAssetModal() {
    document.getElementById('addAssetModal').style.display = 'flex';
    setTimeout(() => document.getElementById('asset-ticker').focus(), 50);
}

function closeAddAssetModal() {
    document.getElementById('addAssetModal').style.display = 'none';
    document.getElementById('asset-ticker').value = '';
    document.getElementById('asset-quantity').value = '';
    document.getElementById('asset-price').value = '';
}

async function handleAddAsset(event) {
    event.preventDefault();

    const ticker = document.getElementById('asset-ticker').value.trim().toUpperCase();
    const quantity = document.getElementById('asset-quantity').value;
    const price = document.getElementById('asset-price').value;

    console.log('[Asset] Adicionando:', { ticker, quantity, price, portfolioId });

    if (!ticker || !quantity || !price) {
        return showNotification('Todos os campos são obrigatórios', 'error');
    }

    try {
        console.log('[Asset] Enviando para API...');
        const novo = await createAsset(portfolioId, ticker, quantity, price);
        console.log('[Asset] Respostada API:', novo);

        currentAssets.push(novo);
        renderAssets();
        closeAddAssetModal();
        showNotification(`${ticker} adicionado com sucesso! Dados da BRAPI sincronizados.`, 'success');
    } catch (err) {
        console.error('[Asset] Erro:', err);
        showNotification('Erro ao adicionar asset: ' + err.message, 'error');
    }
}

// Preview em tempo real dos dados do ticker
let previewTimeout;
document.addEventListener('DOMContentLoaded', () => {
    const tickerInput = document.getElementById('asset-ticker');
    if (tickerInput) {
        tickerInput.addEventListener('input', () => {
            clearTimeout(previewTimeout);
            const previewDiv = document.getElementById('ticker-preview');
            const ticker = tickerInput.value.trim().toUpperCase();

            if (!ticker || ticker.length < 4) {
                if (previewDiv) previewDiv.style.display = 'none';
                return;
            }

            previewTimeout = setTimeout(async () => {
                try {
                    const data = await getAssetDetails(ticker);
                    if (data && !data.error) {
                        const preview = `
                            <div style="background:#f0f8ff;border-left:4px solid #3b5bdb;padding:12px;border-radius:6px;margin-top:8px;">
                                <p style="margin:0;font-size:.75rem;color:#666;font-weight:600;">DADOS DA BRAPI</p>
                                <p style="margin:4px 0;font-weight:600;color:#1a1a1a;">${data.longName || data.shortName || ticker}</p>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px;font-size:.8rem;">
                                    <div><span style="color:#888;">Setor:</span> ${data.sector || '-'}</div>
                                    <div><span style="color:#888;">Preço:</span> R$ ${data.price?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '-'}</div>
                                </div>
                            </div>
                        `;
                        if (previewDiv) {
                            previewDiv.innerHTML = preview;
                            previewDiv.style.display = 'block';
                        }
                    }
                } catch (err) {
                    console.log('Preview não disponível:', err);
                }
            }, 500);
        });
    }
});

async function confirmDeleteAsset(assetId, ticker) {
    if (!confirm(`Excluir ${ticker} do portfólio?`)) return;
    try {
        await deleteAsset(assetId);
        currentAssets = currentAssets.filter(a => a.id !== assetId);
        renderAssets();
        showNotification(`${ticker} excluído`, 'success');
    } catch (err) {
        showNotification('Erro ao excluir asset: ' + err.message, 'error');
    }
}

async function openAssetDetailsModal(ticker) {
    const modal = document.getElementById('assetDetailsModal');
    const content = document.getElementById('assetDetailsContent');

    modal.classList.add('show');
    content.innerHTML = '<p style="text-align:center;padding:20px;">Carregando...</p>';

    try {
        const details = await getAssetDetails(ticker);
        if (!details) {
            throw new Error('Dados não encontrados');
        }

        const change = details.regularMarketChange || 0;
        const changePercent = details.regularMarketChangePercent || 0;
        const changeColor = change >= 0 ? '#10b981' : '#ef4444';
        const changeSign = change >= 0 ? '+' : '';

        content.innerHTML = `
            <div class="asset-details-header">
                <div>
                    <h2>${details.symbol}</h2>
                    <p class="asset-details-name">${details.longName}</p>
                </div>
                ${details.logourl ? `<img src="${details.logourl}" alt="${details.symbol}" style="width:60px;height:60px;border-radius:8px;">` : ''}
            </div>
            
            <div class="asset-details-price">
                <div class="price-current">
                    <p class="label">Preço Atual</p>
                    <h3>R$ ${parseFloat(details.regularMarketPrice || 0).toFixed(2)}</h3>
                    <p class="change" style="color:${changeColor};">
                        ${changeSign}R$ ${Math.abs(change).toFixed(2)} (${changeSign}${Math.abs(changePercent).toFixed(2)}%)
                    </p>
                </div>
            </div>
            
            <div class="asset-details-grid">
                <div class="detail-item">
                    <p class="label">Abertura</p>
                    <p class="value">R$ ${parseFloat(details.regularMarketOpen || 0).toFixed(2)}</p>
                </div>
                <div class="detail-item">
                    <p class="label">Mínima do dia</p>
                    <p class="value">R$ ${parseFloat(details.regularMarketDayLow || 0).toFixed(2)}</p>
                </div>
                <div class="detail-item">
                    <p class="label">Máxima do dia</p>
                    <p class="value">R$ ${parseFloat(details.regularMarketDayHigh || 0).toFixed(2)}</p>
                </div>
                <div class="detail-item">
                    <p class="label">Média 52 semanas</p>
                    <p class="value">R$ ${parseFloat(details.fiftyTwoWeekLow || 0).toFixed(2)} - R$ ${parseFloat(details.fiftyTwoWeekHigh || 0).toFixed(2)}</p>
                </div>
                <div class="detail-item">
                    <p class="label">Volume</p>
                    <p class="value">${(details.regularMarketVolume || 0).toLocaleString('pt-BR')}</p>
                </div>
                <div class="detail-item">
                    <p class="label">P/L</p>
                    <p class="value">${parseFloat(details.priceEarnings || 0).toFixed(2)}</p>
                </div>
            </div>
            
            <div class="asset-details-footer">
                <p class="timestamp">Atualizado em: ${new Date(details.regularMarketTime).toLocaleString('pt-BR')}</p>
            </div>
        `;
    } catch (err) {
        content.innerHTML = `<p style="text-align:center;padding:20px;color:#ef4444;">😢 ${err.message}</p>`;
    }
}

function closeAssetDetailsModal() {
    document.getElementById('assetDetailsModal').classList.remove('show');
}

window.addEventListener('click', e => {
    if (e.target.classList.contains('modal')) e.target.style.display = 'none';
});

function showNotification(message, type = 'success') {
    const el = document.createElement('div');
    el.className = `notification ${type}`;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4000);
}
