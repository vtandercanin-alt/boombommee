/* KRAKEN CASE — Mini App frontend logic */

const KrakenApp = (() => {
    // Telegram WebApp SDK
    const tg = window.Telegram?.WebApp;
    if (tg) {
        tg.ready();
        tg.expand();
    }

    // State
    let initData = '';
    let currentBalance = 0;

    // --- Helpers ---

    function $(id) { return document.getElementById(id); }

    function showScreen(name) {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        const screen = $('screen-' + name);
        if (screen) screen.classList.add('active');

        // Update nav
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        const navBtn = document.querySelector(`.nav-btn[data-screen="${name}"]`);
        if (navBtn) navBtn.classList.add('active');
    }

    async function apiPost(endpoint, body) {
        try {
            const resp = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            if (resp.status === 401) {
                setError('Не авторизован. Открой Mini App через бота.');
                return null;
            }
            if (resp.status === 402) {
                const data = await resp.json();
                setError(`Недостаточно звёзд. Нужно ${data.price}⭐, у тебя ${data.balance.toFixed(0)}⭐`);
                return null;
            }
            if (!resp.ok) {
                const data = await resp.json().catch(() => ({}));
                setError(data.error || 'Ошибка сервера');
                return null;
            }
            return await resp.json();
        } catch (e) {
            setError('Нет связи с сервером');
            return null;
        }
    }

    async function apiGet(endpoint) {
        try {
            const resp = await fetch(endpoint);
            if (!resp.ok) return null;
            return await resp.json();
        } catch (e) {
            return null;
        }
    }

    function setError(text) {
        $('error-text').textContent = text;
        showScreen('error');
    }

    function updateUI(data) {
        if (!data) return;
        currentBalance = data.balance || 0;
        $('balance').textContent = currentBalance.toFixed(0) + '⭐';
        $('stat-cases').textContent = data.cases_opened || 0;
        $('stat-rank').textContent = data.rank || 'Bronze';
    }

    // --- Public functions ---

    async function init() {
        if (tg && tg.initData) {
            initData = tg.initData;
        }

        // Load user data
        const data = await apiPost('/api/me', { init_data: initData });
        if (data) {
            updateUI(data);
        }

        showScreen('home');
    }

    function showHome() {
        showScreen('home');
    }

    async function openCase() {
        const data = await apiPost('/api/open_case', {
            init_data: initData,
            case_type: 'test',
        });
        if (!data) return;

        // Show result
        const icon = data.profit >= 0 ? '🎉' : '😔';
        $('result-icon').textContent = icon;
        $('result-title').textContent = 'Кейс открыт!';
        $('result-reward').textContent = '+' + data.reward.toFixed(0) + ' ⭐';

        const profitEl = $('result-profit');
        if (data.profit > 0) {
            profitEl.textContent = '+' + data.profit.toFixed(0) + ' ⭐ (прибыль!)';
            profitEl.className = 'result-profit positive';
        } else if (data.profit < 0) {
            profitEl.textContent = data.profit.toFixed(0) + ' ⭐ (убыток)';
            profitEl.className = 'result-profit negative';
        } else {
            profitEl.textContent = '0 ⭐ (без изменений)';
            profitEl.className = 'result-profit neutral';
        }

        updateUI({ balance: data.balance, rank: data.rank });
        showScreen('result');
    }

    async function showLeaderboard() {
        showScreen('leaderboard');
        const data = await apiGet('/api/leaderboard');
        const container = $('leaderboard-list');
        container.innerHTML = '';

        if (!data || !data.leaderboard || data.leaderboard.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:20px;">Пока нет данных 🏗️</p>';
            return;
        }

        const medals = ['🥇', '🥈', '🥉'];
        data.leaderboard.forEach((entry, i) => {
            const cls = i < 3 ? ` top-${i + 1}` : '';
            const place = i < 3 ? medals[i] : `${i + 1}️⃣`;
            const div = document.createElement('div');
            div.className = 'lb-entry' + cls;
            div.innerHTML = `
                <span class="lb-place">${place}</span>
                <span class="lb-name">${entry.first_name || entry.username || 'Игрок'}</span>
                <span class="lb-earned">${entry.total_earned.toFixed(0)}⭐</span>
            `;
            container.appendChild(div);
        });
    }

    // Init on load
    document.addEventListener('DOMContentLoaded', init);

    return { showHome, openCase, showLeaderboard };
})();
