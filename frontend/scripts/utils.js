// ── Utilidades generales ─────────────────────────────────────────

function mostrarToast(mensaje, tipo = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${tipo}`;
  toast.textContent = mensaje;
  container.appendChild(toast);
  setTimeout(() => toast.classList.add('visible'), 10);
  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 350);
  }, 3200);
}

// Auto-refresco cada 30 segundos
function iniciarAutoRefresh() {
  setInterval(async () => {
    await cargarDestinos();
    await cargarAlertas();
  }, 30000);
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
  const navbar = document.getElementById('navbar');
  if (window.scrollY > 20) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});
