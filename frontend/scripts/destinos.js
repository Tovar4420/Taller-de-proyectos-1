// ── Lógica de destinos turísticos ───────────────────────────────

async function cargarDestinos(categoria = '') {
  try {
    const path = categoria ? `/destinos?categoria=${categoria}` : '/destinos';
    const data = await apiGet(path);
    destinos = data.destinos;
    renderDestinos(destinos);
    actualizarMetricas(destinos);
    actualizarHeroStats(destinos);
  } catch (err) {
    mostrarToast('Error al cargar destinos', 'error');
  }
}

function actualizarMetricas(lista) {
  const counts = { bajo: 0, moderado: 0, alto: 0, critico: 0 };
  lista.forEach(d => counts[d.estado] = (counts[d.estado] || 0) + 1);
  const q = id => document.getElementById(id);
  q('metric-bajo').textContent     = counts.bajo;
  q('metric-moderado').textContent = counts.moderado;
  q('metric-alto').textContent     = counts.alto;
  q('metric-critico').textContent  = counts.critico;
}

function actualizarHeroStats(lista) {
  const totalVisitantes = lista.reduce((s, d) => s + d.visitantes_actuales, 0);
  document.getElementById('stat-destinos').textContent   = lista.length;
  document.getElementById('stat-visitantes').textContent = totalVisitantes;
}

function renderDestinos(lista) {
  const contenedor = document.getElementById('lista-destinos');
  contenedor.innerHTML = '';

  if (lista.length === 0) {
    contenedor.innerHTML = '<p class="empty-msg">No se encontraron destinos.</p>';
    return;
  }

  const iconos = { Natural: '🌿', Cultural: '🏘️', Histórico: '🏛️' };

  lista.forEach((d, i) => {
    const card = document.createElement('div');
    card.className = `destino-card estado-${d.estado}`;
    card.style.animationDelay = `${i * 0.07}s`;
    card.innerHTML = `
      <div class="card-imagen-placeholder">
        ${iconos[d.categoria] || '🗺️'}
      </div>
      <div class="card-body">
        <div class="card-top">
          <span class="categoria-badge badge-${d.categoria.toLowerCase()}">${d.categoria}</span>
          <span class="estado-badge estado-${d.estado}">${estadoLabel(d.estado)}</span>
        </div>
        <h3 class="card-title">${d.nombre}</h3>
        <p class="card-ubicacion">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          ${d.ubicacion}
        </p>
        <p class="card-desc">${d.descripcion}</p>
        <div class="card-afluencia">
          <div class="afluencia-top">
            <span>${d.visitantes_actuales} / ${d.capacidad_max} visitantes</span>
            <span class="afluencia-pct">${d.porcentaje_ocupacion}%</span>
          </div>
          <div class="barra-fondo">
            <div class="barra-relleno estado-barra-${d.estado}" style="width:${d.porcentaje_ocupacion}%"></div>
          </div>
        </div>
        <div class="card-actions">
          <button onclick="abrirDetalleDestino('${d.id}')" class="btn-detalle">Ver detalle</button>
          ${currentProfile ? `
            <button onclick="registrarVisitaRapida('${d.id}')" class="btn-visita"
              ${d.estado === 'critico' ? 'disabled' : ''}>
              ${d.estado === 'critico' ? '🚫 Lleno' : '✅ Registrar visita'}
            </button>` : ''}
        </div>
      </div>
    `;
    contenedor.appendChild(card);
  });
}

function estadoLabel(estado) {
  return { bajo: '🟢 Bajo', moderado: '🟡 Moderado', alto: '🟠 Alto', critico: '🔴 Crítico' }[estado] || estado;
}

async function abrirDetalleDestino(id) {
  try {
    const d = await apiGet(`/destinos/${id}`);
    const q = s => document.getElementById(s);
    q('detalle-nombre').textContent      = d.nombre;
    q('detalle-ubicacion').textContent   = `📍 ${d.ubicacion}`;
    q('detalle-categoria').className     = `categoria-badge badge-${d.categoria.toLowerCase()}`;
    q('detalle-categoria').textContent   = d.categoria;
    q('detalle-estado').textContent      = estadoLabel(d.estado);
    q('detalle-estado').className        = `estado-badge estado-${d.estado}`;
    q('detalle-descripcion').textContent = d.descripcion;
    q('detalle-visitantes').textContent  = `${d.visitantes_actuales} / ${d.capacidad_max}`;
    q('detalle-porcentaje').textContent  = `${d.porcentaje_ocupacion}%`;

    const barra = q('detalle-barra');
    barra.style.width = `${d.porcentaje_ocupacion}%`;
    barra.className   = `barra-relleno estado-barra-${d.estado}`;

    const btnVisita = q('detalle-btn-visita');
    if (currentProfile) {
      btnVisita.style.display = 'inline-flex';
      btnVisita.disabled      = d.estado === 'critico';
      btnVisita.innerHTML     = d.estado === 'critico'
        ? '🚫 Sin capacidad'
        : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg> Registrar visita`;
      btnVisita.onclick = () => registrarVisitaRapida(d.id);
    } else {
      btnVisita.style.display = 'none';
    }

    q('modal-detalle').classList.add('show');
  } catch (err) {
    mostrarToast('Error al cargar detalle', 'error');
  }
}

function cerrarDetalleDestino() {
  document.getElementById('modal-detalle').classList.remove('show');
}

async function registrarVisitaRapida(destinoId) {
  if (!currentProfile) {
    mostrarToast('Debes iniciar sesión para registrar una visita', 'warning');
    return;
  }
  try {
    const data = await apiPost(`/destinos/${destinoId}/visita`, {
      perfil_id: currentProfile.id,
      cantidad: 1
    });
    mostrarToast(`Visita registrada en ${data.destino.nombre} ✓`, 'success');
    cerrarDetalleDestino();
    await cargarDestinos();
    await cargarAlertas();
  } catch (err) {
    mostrarToast(err.error || 'Error al registrar visita', 'error');
  }
}

function filtrarPorCategoria(cat) {
  document.querySelectorAll('.btn-filtro').forEach(b => b.classList.remove('activo'));
  event.target.classList.add('activo');
  cargarDestinos(cat);
}

function buscarDestino() {
  const termino = document.getElementById('input-busqueda').value.toLowerCase().trim();
  if (!termino) { renderDestinos(destinos); return; }
  const filtrados = destinos.filter(d =>
    d.nombre.toLowerCase().includes(termino) ||
    d.ubicacion.toLowerCase().includes(termino)
  );
  renderDestinos(filtrados);
}
