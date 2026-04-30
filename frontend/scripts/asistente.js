/* ══════════════════════════════════════════════════════════════
   WAYRA — Asistente IA de Turismo Sostenible Junín
   Integrado con Groq API (gratuito) — Llama 3.3 70B
══════════════════════════════════════════════════════════════ */

// ── Estado del asistente ─────────────────────────────────────────
const ASISTENTE = {
  abierto:   false,
  historial: [],
  cargando:  false,
};

// ══ CONFIGURACIÓN — pon tu Groq API key aquí ══════════════════════
const GROQ_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'; //API KEY
// ═════════════════════════════════════════════════════════════════

const QUICK_REPLIES_INICIAL = [
  { label: '🌿 Destinos naturales',     texto: '¿Qué destinos naturales me recomiendas?' },
  { label: '🏛️ Destinos históricos',    texto: '¿Cuáles son los destinos históricos?' },
  { label: '📊 ¿Cuál está disponible?', texto: '¿Qué destinos tienen baja afluencia ahora?' },
  { label: '🗺️ Consejos de viaje',      texto: 'Dame consejos para visitar Junín' },
  { label: '🌡️ ¿Cuál evitar hoy?',     texto: '¿Qué destinos tienen alta ocupación ahora?' },
];

// ── Toggle ventana ───────────────────────────────────────────────
function toggleAsistente() {
  const ventana   = document.getElementById('ai-chat-window');
  const burbuja   = document.getElementById('ai-bubble');
  const iconOpen  = burbuja.querySelector('.ai-icon-open');
  const iconClose = burbuja.querySelector('.ai-icon-closed');
  const ping      = burbuja.querySelector('.ai-bubble-ping');

  ASISTENTE.abierto = !ASISTENTE.abierto;

  if (ASISTENTE.abierto) {
    ventana.style.display       = 'flex';
    ventana.style.flexDirection = 'column';
    burbuja.classList.add('open');
    iconOpen.style.display  = 'flex';
    iconClose.style.display = 'none';
    if (ping) ping.style.display = 'none';

    if (ASISTENTE.historial.length === 0) mostrarMensajeBienvenida();

    setTimeout(() => {
      document.getElementById('ai-input').focus();
      scrollMensajes();
    }, 100);
  } else {
    ventana.style.display = 'none';
    burbuja.classList.remove('open');
    iconOpen.style.display  = 'none';
    iconClose.style.display = 'flex';
  }
}

// ── Bienvenida inicial ───────────────────────────────────────────
function mostrarMensajeBienvenida() {
  agregarMensaje('bot',
    '¡Hola! Soy <strong>Wayra</strong>, tu guía turístico de la región Junín 🌿<br/><br/>' +
    'Puedo recomendarte destinos según tus intereses, contarte sobre la afluencia actual ' +
    'y ayudarte a planificar tu visita. ¿En qué te ayudo hoy?'
  );
  mostrarQuickReplies(QUICK_REPLIES_INICIAL);
}

// ── Enviar mensaje ───────────────────────────────────────────────
async function enviarMensajeIA(textoDirecto = null) {
  if (ASISTENTE.cargando) return;

  const input = document.getElementById('ai-input');
  const texto = (textoDirecto || input.value).trim();
  if (!texto) return;

  input.value = '';
  ocultarQuickReplies();
  agregarMensaje('user', texto);
  ASISTENTE.historial.push({ role: 'user', content: texto });
  ASISTENTE.cargando = true;

  const typingId = mostrarTyping();

  try {
    const contextoDestinos = construirContextoDestinos();

    const systemPrompt = `Eres Wayra, un asistente turístico experto en la región Junín, Perú.
Tu personalidad es cálida, entusiasta y conocedora de la cultura andina y amazónica de Junín.
Ayudas a los visitantes a elegir destinos según sus intereses y la disponibilidad actual.

DATOS EN TIEMPO REAL DE LOS DESTINOS (actualizado ahora):
${contextoDestinos}

INSTRUCCIONES:
- Responde siempre en español, de forma amigable y concisa (máximo 3 párrafos).
- Usa emojis con moderación para hacer la respuesta más visual.
- Cuando recomiendes destinos, menciona su estado de afluencia actual.
- Si un destino está en estado "critico" (>=90%), desaconseja visitarlo hoy.
- Si el destino está "alto" (70-89%), sugiere alternativas o ir temprano.
- Adapta tus recomendaciones al interés del usuario (naturaleza, historia, cultura).
- No uses markdown con asteriscos, usa HTML simple si necesitas énfasis: <strong>, <em>, <br/>.
- Al final de tu respuesta incluye una línea que empiece exactamente con:
  SUGERENCIAS: opción1 | opción2 | opción3
  (máximo 3 sugerencias cortas de seguimiento, sin emojis en las sugerencias)`;

    const respuesta = await llamarGroqAPI(systemPrompt, ASISTENTE.historial);

    quitarTyping(typingId);

    const { mensajeTexto, sugerencias } = parsearRespuesta(respuesta);
    ASISTENTE.historial.push({ role: 'assistant', content: respuesta });
    agregarMensaje('bot', mensajeTexto);

    if (sugerencias.length > 0) {
      mostrarQuickReplies(sugerencias.map(s => ({ label: s, texto: s })));
    }

  } catch (err) {
    quitarTyping(typingId);
    agregarMensaje('bot',
      '¡Ups! Tuve un problema al conectarme 😅 Verifica tu API key de Groq o intenta de nuevo.'
    );
    console.error('Error Wayra:', err);
  } finally {
    ASISTENTE.cargando = false;
    scrollMensajes();
  }
}

// ── Llamada a Groq API ───────────────────────────────────────────
async function llamarGroqAPI(systemPrompt, historial) {
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${GROQ_API_KEY}`,
    },
    body: JSON.stringify({
      model:      'llama-3.3-70b-versatile',
      max_tokens: 1000,
      temperature: 0.7,
      messages: [
        { role: 'system', content: systemPrompt },
        ...historial,
      ],
    }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error?.message || 'Error Groq API');
  }

  const data = await response.json();
  return data.choices[0]?.message?.content || '';
}

// ── Contexto de destinos en tiempo real ─────────────────────────
function construirContextoDestinos() {
  if (!destinos || destinos.length === 0) {
    return 'No hay datos de destinos disponibles en este momento.';
  }
  return destinos.map(d =>
    `• ${d.nombre} (${d.ubicacion}) — Categoría: ${d.categoria} — ` +
    `Ocupación: ${d.visitantes_actuales}/${d.capacidad_max} (${d.porcentaje_ocupacion}%) — ` +
    `Estado: ${d.estado.toUpperCase()}`
  ).join('\n');
}

// ── Parsear respuesta y sugerencias ─────────────────────────────
function parsearRespuesta(texto) {
  const lineas        = texto.split('\n');
  const sugerencias   = [];
  const mensajeLineas = [];

  for (const linea of lineas) {
    if (linea.startsWith('SUGERENCIAS:')) {
      linea.replace('SUGERENCIAS:', '').trim().split('|').forEach(s => {
        const limpio = s.trim();
        if (limpio) sugerencias.push(limpio);
      });
    } else {
      mensajeLineas.push(linea);
    }
  }

  return { mensajeTexto: mensajeLineas.join('\n').trim(), sugerencias };
}

// ── UI helpers ───────────────────────────────────────────────────
function agregarMensaje(rol, html) {
  const contenedor = document.getElementById('ai-messages');
  const wrap       = document.createElement('div');
  wrap.className   = `ai-msg ai-msg-${rol}`;

  const avatarHTML = rol === 'bot'
    ? `<div class="ai-msg-avatar">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2a8 8 0 0 1 8 8c0 5.4-8 14-8 14S4 15.4 4 10a8 8 0 0 1 8-8z"/>
          <circle cx="12" cy="10" r="2.5" fill="currentColor" stroke="none"/>
        </svg>
       </div>`
    : `<div class="ai-msg-avatar" style="background:var(--green-mid);border-color:var(--green-mid);color:white">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
        </svg>
       </div>`;

  wrap.innerHTML = `${avatarHTML}<div class="ai-msg-bubble">${html}</div>`;
  contenedor.appendChild(wrap);
  scrollMensajes();
}

function mostrarTyping() {
  const contenedor = document.getElementById('ai-messages');
  const id         = 'typing-' + Date.now();
  const wrap       = document.createElement('div');
  wrap.className   = 'ai-msg ai-msg-bot ai-typing';
  wrap.id          = id;
  wrap.innerHTML   = `
    <div class="ai-msg-avatar">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2a8 8 0 0 1 8 8c0 5.4-8 14-8 14S4 15.4 4 10a8 8 0 0 1 8-8z"/>
        <circle cx="12" cy="10" r="2.5" fill="currentColor" stroke="none"/>
      </svg>
    </div>
    <div class="ai-msg-bubble">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>`;
  contenedor.appendChild(wrap);
  scrollMensajes();
  return id;
}

function quitarTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function mostrarQuickReplies(opciones) {
  const contenedor    = document.getElementById('ai-quick-replies');
  contenedor.innerHTML = opciones.map(op =>
    `<button class="ai-quick-reply" onclick="enviarMensajeIA('${op.texto.replace(/'/g, "\\'")}')">
      ${op.label}
    </button>`
  ).join('');
}

function ocultarQuickReplies() {
  document.getElementById('ai-quick-replies').innerHTML = '';
}

function scrollMensajes() {
  const c = document.getElementById('ai-messages');
  if (c) c.scrollTop = c.scrollHeight;
}
