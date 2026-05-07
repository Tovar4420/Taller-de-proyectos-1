// ── Capa de comunicación con el backend ──────────────────────────
async function apiGet(path) {
  const res = await fetch(API_BASE + path);
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}

async function apiDelete(path) {
  const res = await fetch(API_BASE + path, { method: 'DELETE' });
  const data = await res.json();
  if (!res.ok) throw data;
  return data;
}
