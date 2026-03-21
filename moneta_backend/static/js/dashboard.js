/**
 * dashboard.js — Moneta
 */

let portfolios = [];
let tokenCheckAttempted = false;

document.addEventListener('DOMContentLoaded', initDashboard);

async function initDashboard() {
    try {
        console.log('[DASHBOARD] Iniciando dashboard...');
        console.log('[DASHBOARD] ACCESS_TOKEN existe?', !!ACCESS_TOKEN);

        // Se não tem token e ainda não tentou buscar, buscar da API
        if (!ACCESS_TOKEN && !tokenCheckAttempted) {
            console.log('[DASHBOARD] Tentando obter token via sessão...');
            tokenCheckAttempted = true;
            const success = await fetchTokenFromSession();
            console.log('[DASHBOARD] Resultado de fetchTokenFromSession:', success);

            if (!success) {
                showNotification('Erro: Sem autenticação. Faça login novamente.', 'error');
                setTimeout(() => window.location.href = '/', 2000);
                return;
            }
        }

        // Se não tem token agora, redirecionar (não ficar em loop)
        if (!ACCESS_TOKEN) {
            console.log('[DASHBOARD] Ainda não tem ACCESS_TOKEN. Redirecionando...');
            showNotification('Erro: Sem autenticação. Faça login novamente.', 'error');
            setTimeout(() => window.location.href = '/', 2000);
            return;
        }

        console.log('[DASHBOARD] Token obtido. Carregando portfólios...');
        await loadPortfolios();
        console.log('[DASHBOARD] Dashboard carregado com sucesso');
    } catch (err) {
        console.error('[DASHBOARD] Erro ao inicializar:', err);
        showNotification('Erro ao inicializar dashboard: ' + err.message, 'error');
    }
}

async function fetchTokenFromSession() {
    try {
        console.log('[TOKEN] Buscando token em /auth/session-token/...');
        const response = await fetch('/auth/session-token/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Inclui cookies de sessão
        });

        console.log('[TOKEN] Response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('[TOKEN] Dados recebidos:', !!data.access);

            if (data.access) {
                ACCESS_TOKEN = data.access;
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                console.log('[TOKEN] Token salvo com sucesso');
                return true;
            }
        } else {
            console.error('[TOKEN] Erro na resposta:', response.status, response.statusText);
            const errorData = await response.json().catch(() => ({}));
            console.error('[TOKEN] Detalhes do erro:', errorData);
        }
        return false;
    } catch (err) {
        console.error('[TOKEN] Erro ao buscar token:', err);
        return false;
    }
}

async function loadPortfolios() {
    try {
        console.log('[PORTFOLIOS] GET /portfolios/...');
        portfolios = await getPortfolios();
        console.log('[PORTFOLIOS] Carregados:', portfolios.length);
        renderPortfolios();
        updateCount();
    } catch (err) {
        showNotification('Erro ao carregar portfólios', 'error');
        console.error('[PORTFOLIOS]', err);
    }
}

function renderPortfolios() {
    const grid = document.getElementById('portfolios-grid');

    if (portfolios.length === 0) {
        grid.innerHTML = `
      <div class="empty-state">
        <p style="font-size:1.05rem;font-weight:700;color:#555;margin-bottom:6px;">Nenhum portfólio ainda</p>
        <p>Clique em <strong>+ Novo Portfólio</strong> para começar</p>
      </div>`;
        return;
    }

    grid.innerHTML = portfolios.map(p => {
        const initials = p.name.trim().substring(0, 2).toUpperCase();
        const date = new Date(p.created_at).toLocaleDateString('pt-BR');
        return `
      <a class="portfolio-card" href="/portfolio/?id=${p.id}">
        <div class="portfolio-card-header">
          <div class="portfolio-icon">${initials}</div>
          <div>
            <p class="portfolio-card-name">${p.name}</p>
            <p class="portfolio-card-date">Criado em ${date}</p>
          </div>
        </div>
        <div class="portfolio-card-footer">
          <span>Ver detalhes</span>
          <span class="portfolio-card-arrow">→</span>
        </div>
      </a>`;
    }).join('');
}

function updateCount() {
    const n = portfolios.length;
    document.getElementById('portfolio-count').textContent =
        `${n} portfólio${n !== 1 ? 's' : ''} cadastrado${n !== 1 ? 's' : ''}`;
}

function openCreatePortfolioModal() {
    console.log('[MODAL] Abrindo modal de novo portfólio');
    const modal = document.getElementById('createPortfolioModal');
    modal.style.display = 'flex';
    modal.classList.add('show');
    setTimeout(() => document.getElementById('portfolio-name-input').focus(), 50);
}

function closeCreatePortfolioModal() {
    console.log('[MODAL] Fechando modal de novo portfólio');
    const modal = document.getElementById('createPortfolioModal');
    modal.style.display = 'none';
    modal.classList.remove('show');
    document.getElementById('portfolio-name-input').value = '';
}

async function handleCreatePortfolio(event) {
    event.preventDefault();
    console.log('[CREATE] Iniciando criação de portfólio');
    console.log('[CREATE] ACCESS_TOKEN existe?', !!ACCESS_TOKEN);

    const name = document.getElementById('portfolio-name-input').value.trim();
    console.log('[CREATE] Nome digitado:', name);

    if (!name) {
        console.log('[CREATE] Nome vazio');
        return showNotification('Nome obrigatório', 'error');
    }

    try {
        console.log('[CREATE] Chamando createPortfolio com nome:', name);
        const novo = await createPortfolio(name);
        console.log('[CREATE] Portfólio criado com sucesso:', novo);

        portfolios.push(novo);
        renderPortfolios();
        updateCount();
        closeCreatePortfolioModal();
        showNotification('Portfólio criado com sucesso!', 'success');
    } catch (err) {
        console.error('[CREATE] Erro:', err.message);
        showNotification('Erro ao criar portfólio: ' + err.message, 'error');
    }
}

window.addEventListener('click', e => {
    if (e.target.classList.contains('modal')) e.target.style.display = 'none';
});

/**
 * CONSULTA DE TICKER
 */
async function handleTickerSearch(event) {
    event.preventDefault();
    const ticker = document.getElementById('ticker-search-input').value.trim().toUpperCase();

    if (!ticker) {
        showNotification('Digite um ticker', 'error');
        return;
    }

    try {
        const data = await getAssetDetails(ticker);
        openTickerDetailsModal(data);
        document.getElementById('ticker-search-input').value = '';
    } catch (err) {
        showNotification(`Erro ao buscar ${ticker}: ${err.message}`, 'error');
    }
}

function openTickerDetailsModal(data) {
    const modal = document.getElementById('tickerDetailsModal');
    const content = document.getElementById('tickerDetailsContent');

    // Formatar preço
    const price = data.regularMarketPrice?.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) || 'N/A';

    const change = data.regularMarketChange || 0;
    const changePercent = data.regularMarketChangePercent || 0;
    const changeClass = change >= 0 ? '#059669' : '#dc2626';

    // Formatar dados adicionais
    const open = data.regularMarketOpen?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A';
    const dayLow = data.regularMarketDayLow?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A';
    const dayHigh = data.regularMarketDayHigh?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A';
    const fiftyTwoWeekLow = data.fiftyTwoWeekLow?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A';
    const fiftyTwoWeekHigh = data.fiftyTwoWeekHigh?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A';
    const volume = data.regularMarketVolume ? (data.regularMarketVolume / 1e6).toFixed(1) + 'M' : 'N/A';

    content.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
            <div>
                <h2 style="margin: 0 0 4px 0; font-size: 1.4rem; color: #1a1a1a;">${data.symbol || 'N/A'}</h2>
                <p style="margin: 0; color: #a0a0a0; font-size: .9rem;">${data.longName || data.shortName || 'Empresa'}</p>
            </div>
            ${data.logourl ? `<img src="${data.logourl}" alt="${data.symbol}" style="width: 48px; height: 48px; border-radius: 8px; object-fit: contain;">` : ''}
        </div>
        
        <div style="background: linear-gradient(135deg, #3b5bdb 0%, #2d4bbc 100%); border-radius: 12px; padding: 16px; margin-bottom: 20px; color: white;">
            <div style="font-size: 2rem; font-weight: 800; margin-bottom: 6px;">R$ ${price}</div>
            <div style="font-size: 1rem; color: ${changeClass}; font-weight: 700;">
                ${change >= 0 ? '+' : ''}${change.toFixed(2).replace('.', ',')} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2).replace('.', ',')}%)
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 12px;">
            <div style="background: #f8fafc; border-radius: 10px; padding: 12px; border-left: 3px solid #3b5bdb;">
                <p style="margin: 0 0 4px 0; font-size: .75rem; color: #b0b0b0; text-transform: uppercase; font-weight: 700;">Abertura</p>
                <p style="margin: 0; font-size: 1rem; color: #1a1a1a; font-weight: 700;">R$ ${open}</p>
            </div>
            <div style="background: #f8fafc; border-radius: 10px; padding: 12px; border-left: 3px solid #3b5bdb;">
                <p style="margin: 0 0 4px 0; font-size: .75rem; color: #b0b0b0; text-transform: uppercase; font-weight: 700;">Mínima do Dia</p>
                <p style="margin: 0; font-size: 1rem; color: #1a1a1a; font-weight: 700;">R$ ${dayLow}</p>
            </div>
            <div style="background: #f8fafc; border-radius: 10px; padding: 12px; border-left: 3px solid #3b5bdb;">
                <p style="margin: 0 0 4px 0; font-size: .75rem; color: #b0b0b0; text-transform: uppercase; font-weight: 700;">Máxima do Dia</p>
                <p style="margin: 0; font-size: 1rem; color: #1a1a1a; font-weight: 700;">R$ ${dayHigh}</p>
            </div>
            <div style="background: #f8fafc; border-radius: 10px; padding: 12px; border-left: 3px solid #3b5bdb;">
                <p style="margin: 0 0 4px 0; font-size: .75rem; color: #b0b0b0; text-transform: uppercase; font-weight: 700;">52 Semanas</p>
                <p style="margin: 0; font-size: .9rem; color: #1a1a1a; font-weight: 700;">R$ ${fiftyTwoWeekLow} - R$ ${fiftyTwoWeekHigh}</p>
            </div>
            <div style="background: #f8fafc; border-radius: 10px; padding: 12px; border-left: 3px solid #3b5bdb;">
                <p style="margin: 0 0 4px 0; font-size: .75rem; color: #b0b0b0; text-transform: uppercase; font-weight: 700;">Volume</p>
                <p style="margin: 0; font-size: 1rem; color: #1a1a1a; font-weight: 700;">${volume}</p>
            </div>
            <div style="background: #f8fafc; border-radius: 10px; padding: 12px; border-left: 3px solid #3b5bdb;">
                <p style="margin: 0 0 4px 0; font-size: .75rem; color: #b0b0b0; text-transform: uppercase; font-weight: 700;">Market Cap</p>
                <p style="margin: 0; font-size: 1rem; color: #1a1a1a; font-weight: 700;">${data.marketCap ? (data.marketCap / 1e9).toFixed(1) + 'B' : 'N/A'}</p>
            </div>
        </div>
        
        <p style="text-align: center; color: #b0b0b0; font-size: .75rem; margin-top: 16px;">
            Atualizado em: ${new Date().toLocaleTimeString('pt-BR')}
        </p>
    `;

    modal.style.display = 'flex';
    modal.classList.add('show');
}

function closeTickerDetailsModal() {
    const modal = document.getElementById('tickerDetailsModal');
    modal.style.display = 'none';
    modal.classList.remove('show');
}

function showNotification(message, type = 'success') {
    const el = document.createElement('div');
    el.className = `notification ${type}`;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 4000);
}
