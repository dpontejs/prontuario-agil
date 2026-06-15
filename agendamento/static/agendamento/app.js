// ── Auth guard ──────────────────────────────────────────────
(function () {
  const publicPaths = ['/login/'];
  if (!publicPaths.includes(window.location.pathname) && !localStorage.getItem('access')) {
    window.location.href = '/login/';
  }
})();

// ── Logout ───────────────────────────────────────────────────
function logout() {
  ['access', 'refresh', 'username', 'is_medico', 'is_paciente', 'is_superuser', 'paciente_id', 'medico_id'].forEach(k => localStorage.removeItem(k));
  window.location.href = '/login/';
}

// ── authFetch: fetch com Bearer token, redireciona em 401 ────
async function authFetch(url, opts = {}) {
  const token = localStorage.getItem('access');
  const res = await fetch(url, {
    ...opts,
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', ...(opts.headers || {}) },
  });
  if (res.status === 401) { window.location.href = '/login/'; }
  return res;
}

// ── Popula navbar com username e controla link prontuário ────
(async function initNav() {
  const token = localStorage.getItem('access');
  if (!token) return;

  // Username no nav
  const usernameEl = document.getElementById('nav-username');
  const cachedName = localStorage.getItem('username');
  if (usernameEl && cachedName) usernameEl.textContent = cachedName;

  // Tenta carregar info do usuário se não estiver em cache
  if (!localStorage.getItem('is_medico')) {
    try {
      const res = await authFetch('/api/me/');
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('username',     data.username);
        localStorage.setItem('is_medico',    data.is_medico    ? '1' : '0');
        localStorage.setItem('is_paciente',  data.is_paciente  ? '1' : '0');
        localStorage.setItem('is_superuser', data.is_superuser ? '1' : '0');
        if (data.paciente_id) localStorage.setItem('paciente_id', data.paciente_id);
        if (data.medico_id)   localStorage.setItem('medico_id',   data.medico_id);
        if (usernameEl) usernameEl.textContent = data.username;

        // Admin sem papel clínico não usa a interface web
        if (!data.is_medico && !data.is_paciente) {
          window.location.href = '/admin/';
          return;
        }
      }
    } catch (_) {}
  }

  const isMedico  = localStorage.getItem('is_medico')  === '1';
  const path = window.location.pathname;

  const navAgendar  = document.getElementById('nav-agendar');
  const navMeusAg   = document.getElementById('nav-meus-agendamentos');
  const navPront    = document.getElementById('nav-prontuario');

  if (isMedico) {
    // Médico: mostra Prontuários e Agenda (com label diferente), bloqueia apenas /agendar/
    if (navPront) navPront.style.display = 'inline';
    if (navMeusAg) { navMeusAg.style.display = 'inline'; navMeusAg.textContent = 'Agenda'; }
    if (path === '/agendar/') {
      window.location.href = '/';
      return;
    }
  } else {
    // Paciente: mostra Agendar e Meus Agendamentos, bloqueia Prontuários
    if (navAgendar) navAgendar.style.display = 'inline';
    if (navMeusAg)  navMeusAg.style.display  = 'inline';
    if (path === '/prontuario/') {
      window.location.href = '/';
      return;
    }
  }

  // Marca link ativo
  document.querySelectorAll('.navbar-links a').forEach(a => {
    if (a.href && window.location.pathname.startsWith(new URL(a.href).pathname) && a.href !== '/') {
      a.classList.add('ativo');
    }
    if (window.location.pathname === '/' && a.getAttribute('href') === '/') {
      a.classList.add('ativo');
    }
  });
})();
