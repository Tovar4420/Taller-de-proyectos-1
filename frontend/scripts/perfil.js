// ── Lógica de perfiles ───────────────────────────────────────────

function abrirModalPerfil() {
  document.getElementById('modal-perfil').classList.add('show');
  document.getElementById('perfil-error').textContent = '';
  if (currentProfile) {
    mostrarInfoPerfil();
  } else {
    mostrarFormLogin();
  }
}

function cerrarModalPerfil() {
  document.getElementById('modal-perfil').classList.remove('show');
}

function mostrarFormLogin() {
  document.getElementById('form-login').style.display = 'block';
  document.getElementById('form-crear').style.display = 'none';
  document.getElementById('info-perfil').style.display = 'none';
}

function mostrarFormCrear() {
  document.getElementById('form-login').style.display = 'none';
  document.getElementById('form-crear').style.display = 'block';
  document.getElementById('info-perfil').style.display = 'none';
}

function mostrarInfoPerfil() {
  document.getElementById('form-login').style.display = 'none';
  document.getElementById('form-crear').style.display = 'none';
  document.getElementById('info-perfil').style.display = 'block';
  if (currentProfile) {
    document.getElementById('info-nombre').textContent  = currentProfile.nombre;
    document.getElementById('info-usuario').textContent = '@' + currentProfile.nombre_perfil;
    document.getElementById('info-tipo').textContent    = currentProfile.tipo;
    document.getElementById('info-visitas').textContent = currentProfile.total_visitas || 0;
  }
}

async function loginPerfil() {
  const nombrePerfil = document.getElementById('login-nombre').value.trim();
  if (!nombrePerfil) {
    document.getElementById('perfil-error').textContent = 'Ingresa tu nombre de perfil.';
    return;
  }
  try {
    const data = await apiGet('/perfiles');
    const perfil = data.perfiles.find(p => p.nombre_perfil === nombrePerfil);
    if (!perfil) {
      document.getElementById('perfil-error').textContent = 'Perfil no encontrado.';
      return;
    }
    currentProfile = perfil;
    actualizarBarraPerfil();
    mostrarInfoPerfil();
    mostrarToast(`¡Bienvenido, ${perfil.nombre}!`, 'success');
    await cargarDestinos();
  } catch (err) {
    document.getElementById('perfil-error').textContent = 'Error al iniciar sesión.';
  }
}

async function crearPerfil() {
  const nombre       = document.getElementById('crear-nombre').value.trim();
  const nombrePerfil = document.getElementById('crear-usuario').value.trim();
  document.getElementById('perfil-error').textContent = '';

  if (!nombre || !nombrePerfil) {
    document.getElementById('perfil-error').textContent = 'Completa todos los campos.';
    return;
  }
  try {
    const data = await apiPost('/perfiles', { nombre, nombre_perfil: nombrePerfil, tipo: 'turista' });
    currentProfile = data.perfil;
    actualizarBarraPerfil();
    mostrarInfoPerfil();
    mostrarToast(`Perfil creado. ¡Bienvenido, ${nombre}!`, 'success');
    await cargarDestinos();
  } catch (err) {
    document.getElementById('perfil-error').textContent = err.error || 'Error al crear perfil.';
  }
}

async function eliminarPerfil() {
  if (!currentProfile) return;
  if (!confirm(`¿Eliminar el perfil "${currentProfile.nombre_perfil}"? Esta acción no se puede deshacer.`)) return;
  try {
    await apiDelete(`/perfiles/${currentProfile.id}`);
    mostrarToast('Perfil eliminado', 'info');
    cerrarSesion();
  } catch (err) {
    mostrarToast('Error al eliminar perfil', 'error');
  }
}

function cerrarSesion() {
  currentProfile = null;
  actualizarBarraPerfil();
  cerrarModalPerfil();
  cargarDestinos();
  mostrarToast('Sesión cerrada', 'info');
}

function actualizarBarraPerfil() {
  const span = document.getElementById('barra-perfil');
  const avatar = document.querySelector('.avatar-circle');
  if (currentProfile) {
    span.textContent = currentProfile.nombre_perfil;
    if (avatar) {
      avatar.style.background = 'var(--gold)';
    }
  } else {
    span.textContent = 'Iniciar sesión';
    if (avatar) {
      avatar.style.background = 'var(--gold)';
    }
  }
}
