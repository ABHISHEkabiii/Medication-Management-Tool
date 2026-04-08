/* ─── Medication Management Tool — script.js ─────────── */

const API = "";  // same origin; if separate server use "http://localhost:5000"

// ── Navbar scroll effect ─────────────────────────────
window.addEventListener("scroll", () => {
  document.getElementById("navbar").style.borderBottomColor =
    window.scrollY > 10 ? "rgba(148,163,184,.18)" : "rgba(148,163,184,.1)";
});

// ── Smooth scroll for all anchor links ───────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener("click", e => {
    e.preventDefault();
    const target = document.querySelector(a.getAttribute("href"));
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

// ── Form Validation ───────────────────────────────────
function validateForm() {
  const fields = [
    { id: "name",      label: "Name",      pattern: /\S+/ },
    { id: "email",     label: "Email",     pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
    { id: "medicine",  label: "Medicine",  pattern: /\S+/ },
    { id: "dosage",    label: "Dosage",    pattern: /\S+/ },
    { id: "time",      label: "Time",      pattern: /^\d{2}:\d{2}$/ },
    { id: "frequency", label: "Frequency", pattern: /\S+/ },
  ];
  let valid = true;
  fields.forEach(f => {
    const el  = document.getElementById(f.id);
    const err = document.getElementById(`err-${f.id}`);
    const val = el.value.trim();
    if (!f.pattern.test(val)) {
      el.classList.add("invalid");
      if (err) err.textContent = `${f.label} is required`;
      valid = false;
    } else {
      el.classList.remove("invalid");
      if (err) err.textContent = "";
    }
  });
  return valid;
}

// Clear invalid state on input
["name","email","medicine","dosage","time","frequency"].forEach(id => {
  document.getElementById(id)?.addEventListener("input", () => {
    const el  = document.getElementById(id);
    const err = document.getElementById(`err-${id}`);
    el.classList.remove("invalid");
    if (err) err.textContent = "";
  });
});

// ── Submit Form ───────────────────────────────────────
document.getElementById("medForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  if (!validateForm()) return;

  const btn     = document.getElementById("submitBtn");
  const btnText = document.getElementById("btnText");
  const spinner = document.getElementById("btnSpinner");
  const msg     = document.getElementById("formMessage");

  btn.disabled = true;
  btnText.classList.add("hidden");
  spinner.classList.remove("hidden");
  msg.className = "form-message hidden";

  const payload = {
    name:      document.getElementById("name").value.trim(),
    email:     document.getElementById("email").value.trim(),
    medicine:  document.getElementById("medicine").value.trim(),
    dosage:    document.getElementById("dosage").value.trim(),
    time:      document.getElementById("time").value,
    frequency: document.getElementById("frequency").value,
  };

  try {
    const res  = await fetch(`${API}/api/medications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (res.ok) {
      msg.textContent  = `✅ Reminder set! Confirmation email sent to ${payload.email}`;
      msg.className    = "form-message success";
      this.reset();
      await loadAll();
      setTimeout(() => {
        document.getElementById("dashboard").scrollIntoView({ behavior: "smooth" });
      }, 1200);
    } else {
      msg.textContent = `❌ ${data.error || "Something went wrong. Try again."}`;
      msg.className   = "form-message error";
    }
  } catch {
    msg.textContent = "❌ Cannot reach server. Make sure Flask is running on port 5000.";
    msg.className   = "form-message error";
  }

  btn.disabled = false;
  btnText.classList.remove("hidden");
  spinner.classList.add("hidden");
});

// ── Load Stats ────────────────────────────────────────
async function loadStats() {
  try {
    const res   = await fetch(`${API}/api/stats`);
    if (!res.ok) return;
    const s     = await res.json();
    document.getElementById("statTotal").textContent     = s.total;
    document.getElementById("statTaken").textContent     = s.taken;
    document.getElementById("statMissed").textContent    = s.missed;
    document.getElementById("statAdherence").textContent = s.adherence + "%";
  } catch { /* silent */ }
}

// ── Load Medications Table ────────────────────────────
async function loadMedications() {
  try {
    const res  = await fetch(`${API}/api/medications`);
    if (!res.ok) return;
    const meds = await res.json();
    const tbody = document.getElementById("medBody");

    if (!meds.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="empty">No medications yet. Add one above ↑</td></tr>`;
      return;
    }

    tbody.innerHTML = meds.map(m => {
      const date = m.created_at ? new Date(m.created_at).toLocaleDateString("en-IN",
        { day: "2-digit", month: "short", year: "numeric" }) : "—";
      const status = m.taken
        ? `<span class="pill taken">✓ Taken</span>`
        : `<span class="pill pending">⏳ Pending</span>`;
      const takenbtn = !m.taken
        ? `<button class="act-btn" onclick="markTaken('${esc(m.medicine)}')">Mark taken</button>`
        : "";
      return `
        <tr>
          <td>${esc(m.name)}</td>
          <td><strong>${esc(m.medicine)}</strong></td>
          <td>${esc(m.dosage)}</td>
          <td><span style="color:var(--blue);font-weight:600">${m.time}</span></td>
          <td>${esc(m.frequency)}</td>
          <td>${status}</td>
          <td style="color:var(--text2);font-size:13px">${date}</td>
          <td>
            ${takenbtn}
            <button class="act-btn del" onclick="deleteMed('${esc(m.medicine)}')">Delete</button>
          </td>
        </tr>`;
    }).join("");
  } catch { /* silent */ }
}

// ── Mark Taken ────────────────────────────────────────
async function markTaken(medicine) {
  try {
    const res = await fetch(`${API}/api/medications/${encodeURIComponent(medicine)}/taken`, {
      method: "PATCH"
    });
    if (res.ok) await loadAll();
  } catch { /* silent */ }
}

// ── Delete Medication ─────────────────────────────────
async function deleteMed(medicine) {
  if (!confirm(`Delete "${medicine}"? This cannot be undone.`)) return;
  try {
    await fetch(`${API}/api/medications/${encodeURIComponent(medicine)}`, { method: "DELETE" });
    await loadAll();
  } catch { /* silent */ }
}

// ── Refresh all ───────────────────────────────────────
async function refresh() {
  await loadAll();
}
async function loadAll() {
  await Promise.all([loadStats(), loadMedications()]);
}

// ── Escape HTML ───────────────────────────────────────
function esc(str) {
  return String(str)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ── Init ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadAll();
});

setInterval(loadAll, 60_000);  // auto-refresh every 60s
