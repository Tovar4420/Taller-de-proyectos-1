// ── Inicialización de la aplicación ─────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  await cargarDestinos();
  await cargarAlertas();
  iniciarAutoRefresh();
});

// Cerrar modales al hacer clic fuera
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.remove('show');
  });
});

// Cerrar modales con ESC
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.show').forEach(m => m.classList.remove('show'));
  }
});
