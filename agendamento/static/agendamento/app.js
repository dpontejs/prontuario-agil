// Redireciona para login se não houver token
(function () {
  const publicPaths = ['/login/'];
  if (!publicPaths.includes(window.location.pathname) && !localStorage.getItem('access')) {
    window.location.href = '/login/';
  }
})();

function logout() {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
  window.location.href = '/login/';
}

// Mostra link de prontuário apenas para médicos (tenta GET /api/prontuarios/)
(async function () {
  const token = localStorage.getItem('access');
  if (!token) return;
  const res = await fetch('/api/prontuarios/', {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if (res.ok) {
    const el = document.getElementById('nav-prontuario');
    if (el) el.style.display = 'inline';
  }
})();
