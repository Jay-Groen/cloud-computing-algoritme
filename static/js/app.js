// TrainSmart — Frontend Logic

// Toggle sections
function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.target.classList.add('active');
}

// Day picker toggles
document.querySelectorAll('.dag-btn').forEach(btn => {
    btn.addEventListener('click', () => btn.classList.toggle('selected'));
});

// Collect form data
function getFormData() {
    const blessures = [...document.querySelectorAll('.checkbox-group input:checked')]
        .map(cb => cb.value);

    const dagen = [...document.querySelectorAll('.dag-btn.selected')]
        .map(b => b.dataset.dag);

    return {
        naam: document.getElementById('naam').value.trim() || 'Sporter',
        leeftijd: parseInt(document.getElementById('leeftijd').value) || 25,
        geslacht: document.getElementById('geslacht').value,
        lengte: parseInt(document.getElementById('lengte').value) || 175,
        gewicht: parseFloat(document.getElementById('gewicht').value) || 75,
        trainingsdoel: document.getElementById('trainingsdoel').value,
        trainingsniveau: document.getElementById('trainingsniveau').value,
        trainingsfrequentie: parseInt(document.getElementById('trainingsfrequentie').value),
        trainingsduur: parseInt(document.getElementById('trainingsduur').value),
        activiteitsniveau: document.getElementById('activiteitsniveau').value,
        blessures,
        beschikbare_dagen: dagen.length > 0 ? dagen : ['maandag', 'woensdag', 'vrijdag']
    };
}

// Generate plan
async function genereerPlan() {
    const btn = document.querySelector('.generate-btn');
    const data = getFormData();

    // Validate
    if (!data.naam) {
        showToast('Vul je naam in', 'error');
        return;
    }
    if (data.beschikbare_dagen.length < data.trainingsfrequentie) {
        showToast(`Selecteer minimaal ${data.trainingsfrequentie} beschikbare dagen`, 'error');
        return;
    }

    btn.classList.add('loading');
    btn.querySelector('.btn-text').textContent = 'Bezig...';

    try {
        const response = await fetch('/api/trainingsplan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'API fout');
        }

        const plan = await response.json();
        renderResult(plan);

    } catch (err) {
        showToast(err.message || 'Er is iets misgegaan', 'error');
    } finally {
        btn.classList.remove('loading');
        btn.querySelector('.btn-text').textContent = 'GENEREER MIJN PLAN';
    }
}

// Render result
function renderResult(plan) {
    document.getElementById('r-schema').textContent = plan.schema_type;
    document.getElementById('r-focus').textContent = plan.focus;
    document.getElementById('r-sets').textContent = plan.sets;
    document.getElementById('r-herhalingen').textContent = plan.herhalingen;
    document.getElementById('r-oefeningen').textContent = plan.aantal_oefeningen_per_training;
    document.getElementById('r-rust').textContent = plan.rusttijd;
    document.getElementById('r-intensiteit').textContent = capitalise(plan.intensiteit);
    document.getElementById('r-aanpassing').textContent = plan.activiteitsaanpassing;
    document.getElementById('result-naam').textContent = `voor ${plan.naam}`;
    document.getElementById('result-datum').textContent = plan.aangemaakt_op || new Date().toLocaleDateString('nl-NL');

    // Training days
    const dagenEl = document.getElementById('r-dagen');
    dagenEl.innerHTML = plan.trainingsdagen
        .map(d => `<span class="day-tag">${capitalise(d)}</span>`)
        .join('');

    // Injuries
    const blessureBlock = document.getElementById('r-blessure-block');
    if (plan.vermijd_oefeningen && plan.vermijd_oefeningen.length > 0) {
        document.getElementById('r-vermijd').textContent = plan.vermijd_oefeningen.join(', ');
        blessureBlock.style.display = '';
    } else {
        blessureBlock.style.display = 'none';
    }

    const resultEl = document.getElementById('result-section');
    resultEl.classList.remove('hidden');
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Reset form
function resetForm() {
    document.getElementById('result-section').classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Load history
async function loadHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '<div class="loading">Laden...</div>';

    try {
        const res = await fetch('/api/trainingsplannen');
        const plans = await res.json();

        if (!plans.length) {
            list.innerHTML = `
                <div class="empty-state">
                    <h3>Nog geen plannen opgeslagen</h3>
                    <p>Genereer je eerste trainingsplan!</p>
                </div>`;
            return;
        }

        list.innerHTML = plans.map(p => `
            <div class="history-item">
                <div>
                    <div class="history-naam">${p.naam || 'Onbekend'}</div>
                    <div class="history-meta">
                        <span class="history-tag">${p.schema_type || '-'}</span>
                        <span class="history-tag">${p.trainingsdagen ? p.trainingsdagen.join(', ') : '-'}</span>
                        <span class="history-tag">${p.intensiteit || '-'}</span>
                    </div>
                </div>
                <div class="history-date">${formatDate(p.aangemaakt_op)}</div>
            </div>
        `).join('');

    } catch (err) {
        list.innerHTML = `<div class="loading">Fout bij laden: ${err.message}</div>`;
    }
}

// Utilities
function capitalise(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('nl-NL', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
        return dateStr;
    }
}

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3500);
}
