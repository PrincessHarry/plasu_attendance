/**
 * PLASU Smart Attendance System — Main JS
 * Vanilla JS utilities used across all pages.
 */

'use strict';

/* ── CSRF helper ─────────────────────────────────────────────────────────── */
function getCookie(name) {
  const val = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return val ? val[2] : null;
}

/* ── Live datetime display ───────────────────────────────────────────────── */
function initDatetimeDisplay() {
  const el = document.getElementById('datetime-display');
  if (!el) return;
  function update() {
    const now = new Date();
    el.textContent =
      now.toLocaleDateString('en-NG', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' }) +
      '\u00a0\u00a0' +
      now.toLocaleTimeString('en-NG', { hour: '2-digit', minute: '2-digit' });
  }
  update();
  setInterval(update, 30000);
}

/* ── Auto-dismiss alerts ─────────────────────────────────────────────────── */
function initAlerts() {
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(el => {
    const ms = parseInt(el.dataset.autoDismiss, 10) || 4000;
    setTimeout(() => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, ms);
  });
}

/* ── Confirm-on-submit for delete forms ──────────────────────────────────── */
function initDeleteConfirm() {
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      const msg = form.dataset.confirm || 'Are you sure you want to delete this?';
      if (!window.confirm(msg)) e.preventDefault();
    });
  });
}

/* ── Toggle password visibility ─────────────────────────────────────────── */
function togglePassword(fieldId, btnId) {
  const field = document.getElementById(fieldId);
  const btn   = document.getElementById(btnId);
  if (!field) return;
  if (field.type === 'password') {
    field.type = 'text';
    if (btn) btn.setAttribute('aria-label', 'Hide password');
  } else {
    field.type = 'password';
    if (btn) btn.setAttribute('aria-label', 'Show password');
  }
}

/* ── QR Code generator ───────────────────────────────────────────────────── */
function generateQR(canvasId, url, size) {
  size = size || 220;
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof qrcode === 'undefined') return;
  const qr = qrcode(0, 'M');
  qr.addData(url);
  qr.make();
  const ctx    = canvas.getContext('2d');
  const count  = qr.getModuleCount();
  const cell   = Math.floor(size / count);
  const offset = Math.floor((size - cell * count) / 2);
  ctx.fillStyle = '#F8FAFC';
  ctx.fillRect(0, 0, size, size);
  for (let r = 0; r < count; r++) {
    for (let c = 0; c < count; c++) {
      ctx.fillStyle = qr.isDark(r, c) ? '#14532D' : '#F8FAFC';
      ctx.fillRect(offset + c * cell, offset + r * cell, cell, cell);
    }
  }
}

/* ── Countdown timer ─────────────────────────────────────────────────────── */
function initCountdown(elementId, isoExpiresAt) {
  const el = document.getElementById(elementId);
  if (!el || !isoExpiresAt) return;
  const expires = new Date(isoExpiresAt);
  function tick() {
    const diff = Math.max(0, Math.floor((expires - new Date()) / 1000));
    const m = Math.floor(diff / 60).toString().padStart(2, '0');
    const s = (diff % 60).toString().padStart(2, '0');
    el.textContent = diff > 0 ? m + ':' + s : 'Expired';
    if (diff === 0) { el.style.color = '#EF4444'; clearInterval(timer); }
  }
  tick();
  const timer = setInterval(tick, 1000);
}

/* ── Live attendance poller ──────────────────────────────────────────────── */
function initAttendancePoller(sessionId, options) {
  options = Object.assign({ interval: 3000 }, options || {});
  if (!sessionId) return;

  function poll() {
    fetch('/api/session/' + sessionId + '/count/')
      .then(r => r.json())
      .then(data => {
        // Update count
        const countEl = document.getElementById('live-count');
        if (countEl) countEl.textContent = data.count;

        // Update progress
        const pctEl = document.getElementById('pct');
        if (pctEl) pctEl.textContent = data.count + '/' + (data.enrolled || 0);

        const bar = document.getElementById('progress-bar');
        if (bar && data.enrolled > 0) {
          bar.style.width = Math.round(data.count / data.enrolled * 100) + '%';
        }

        // Update student list
        if (data.students && data.students.length > 0) {
          const emptyState = document.getElementById('empty-state');
          if (emptyState) emptyState.remove();
          const list = document.getElementById('student-list');
          if (list) {
            list.innerHTML = data.students.map(function(s) {
              const inits = s.name.split(' ').map(function(n) { return n[0] || ''; }).join('').toUpperCase().slice(0,2);
              return [
                '<div class="px-6 py-3 flex items-center justify-between border-b border-slate-50 last:border-0">',
                  '<div class="flex items-center gap-3">',
                    '<div class="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-xs font-bold text-primary">' + inits + '</div>',
                    '<div>',
                      '<p class="font-semibold text-sm" style="color:#0f172a">' + s.name + '</p>',
                      '<p class="text-slate-400 text-xs font-mono">' + s.matric + '</p>',
                    '</div>',
                  '</div>',
                  '<div class="text-right">',
                    '<span class="badge badge-green">Present</span>',
                    (s.verified ? '<p class="text-xs text-slate-400 mt-0.5">&#x2713; Verified</p>' : ''),
                    '<p class="text-slate-300 text-xs">' + s.time + '</p>',
                  '</div>',
                '</div>',
              ].join('');
            }).join('');
          }
        }
      })
      .catch(function() {}); // Silently ignore network errors
  }

  poll();
  setInterval(poll, options.interval);
}

/* ── Fingerprint simulation UI ───────────────────────────────────────────── */
const FingerprintUI = {
  states: {
    waiting:  { title: 'Fingerprint Required',    msg: 'Place your finger on the sensor to verify your identity', circleClass: 'fp-waiting'  },
    scanning: { title: 'Scanning Fingerprint...', msg: 'Keep your finger steady on the sensor',                   circleClass: 'fp-scanning' },
    success:  { title: 'Attendance Marked!',      msg: 'Your attendance has been recorded successfully',           circleClass: 'fp-success'  },
    error:    { title: 'Verification Failed',     msg: 'Fingerprint did not match. Please try again.',             circleClass: 'fp-error'    },
  },

  setState: function(state, customMsg) {
    const s = this.states[state] || this.states.waiting;
    const titleEl = document.getElementById('fp-status-title');
    const msgEl   = document.getElementById('fp-status-msg');
    const rings   = document.getElementById('fp-rings');
    const circle  = document.getElementById('fp-circle');

    if (titleEl) titleEl.textContent = s.title;
    if (msgEl)   msgEl.textContent   = customMsg || s.msg;
    if (rings)   rings.classList.toggle('hidden', state !== 'scanning');

    const colorMap = {
      waiting:  { bg: '#f1f5f9', border: '#e2e8f0', icon: '#94a3b8' },
      scanning: { bg: '#f0fdf4', border: '#86efac', icon: '#14532D' },
      success:  { bg: '#f0fdf4', border: '#4ade80', icon: '#22c55e' },
      error:    { bg: '#fef2f2', border: '#fca5a5', icon: '#ef4444' },
    };
    const c = colorMap[state] || colorMap.waiting;
    if (circle) {
      circle.style.background   = c.bg;
      circle.style.borderColor  = c.border;
      const icon = document.getElementById('fp-icon');
      if (icon) icon.style.color = c.icon;
    }
  },
};

/* ── Sidebar mobile toggle ───────────────────────────────────────────────── */
function initMobileSidebar() {
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar   = document.getElementById('sidebar');
  const overlay   = document.getElementById('sidebar-overlay');
  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener('click', function() {
    sidebar.classList.toggle('sidebar-open');
    if (overlay) overlay.classList.toggle('hidden');
  });
  if (overlay) {
    overlay.addEventListener('click', function() {
      sidebar.classList.remove('sidebar-open');
      overlay.classList.add('hidden');
    });
  }
}

/* ── Init on DOM ready ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function() {
  initDatetimeDisplay();
  initAlerts();
  initDeleteConfirm();
  initMobileSidebar();
});

/* ── Expose globals ──────────────────────────────────────────────────────── */
window.PLASU = {
  getCookie,
  generateQR,
  initCountdown,
  initAttendancePoller,
  FingerprintUI,
  togglePassword,
};
