// ── Lógica de alertas ────────────────────────────────────────────

async function cargarAlertas() {
  try {
    const data = await apiGet('/alertas');
    alertas = data.alertas;
    actualizarBadgeAlertas(alertas.length);
    document.getElementById('stat-alertas').textContent = alertas.length;
    return alertas;
  } catch (err) {
    return [];
  }
}

function actualizarBadgeAlertas(n) {
  const badge = document.getElementById('badge-alertas');
  if (n > 0) {
    badge.textContent = n;
    badge.style.display = 'inline-flex';
  } else {
    badge.style.display = 'none';
  }
}

async function abrirPanelAlertas() {
  document.getElementById('modal-alertas').classList.add('show');
  const lista = await cargarAlertas();
  renderAlertas(lista);
}

function cerrarPanelAlertas() {
  document.getElementById('modal-alertas').classList.remove('show');
}

function renderAlertas(lista) {
  const panel = document.getElementById('panel-alertas');
  if (lista.length === 0) {
    panel.innerHTML = `
      <div style="text-align:center; padding:2.5rem; color:var(--gray-400)">
        <div style="font-size:2.5rem; margin-bottom:0.75rem">✅</div>
        <p style="font-size:0.95rem">No hay alertas activas.<br/>Todos los destinos están en buen estado.</p>
      </div>`;
    return;
  }

  panel.innerHTML = lista.map(a => `
    <div class="alerta-item alerta-${a.tipo}">
      <span class="alerta-icono">${a.tipo === 'critica' ? '🔴' : '🟠'}</span>
      <div class="alerta-contenido">
        <strong>${a.destino}</strong>
        <p>${a.mensaje}</p>
        <small>${formatearFecha(a.fecha)}</small>
      </div>
      <button class="btn-resolver" onclick="resolverAlerta('${a.id}')" title="Resolver alerta">✕</button>
    </div>
  `).join('');
}

async function resolverAlerta(id) {
  try {
    await apiDelete(`/alertas/${id}`);
    mostrarToast('Alerta resuelta', 'success');
    const lista = await cargarAlertas();
    renderAlertas(lista);
    await cargarDestinos();
  } catch (err) {
    mostrarToast('Error al resolver alerta', 'error');
  }
}

function formatearFecha(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}
