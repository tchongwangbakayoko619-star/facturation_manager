// static/js/toast.js
import { escapeHtml } from "./utils/helpers.js";

let container;
function getContainer() {
  if (container) return container;
  container = document.createElement("div");
  container.className = "fixed right-4 top-4 z-[60] w-full max-w-sm space-y-3";
  container.setAttribute("aria-live", "polite");
  document.body.append(container);
  return container;
}

// Fonction de base
function showToast(message, type = "info", duration = 4500) {
  const colors = {
    success: "border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200",
    error: "border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-800 dark:bg-rose-950/50 dark:text-rose-200",
    warning: "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200",
    info: "border-blue-200 bg-blue-50 text-blue-900 dark:border-blue-800 dark:bg-blue-950/50 dark:text-blue-200",
  };
  
  const icons = {
    success: `<svg class="h-5 w-5 text-emerald-500 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    error: `<svg class="h-5 w-5 text-rose-500 dark:text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    warning: `<svg class="h-5 w-5 text-amber-500 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`,
    info: `<svg class="h-5 w-5 text-blue-500 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
  };

  const toast = document.createElement("div");
  toast.className = `flex items-start gap-3 rounded-xl border p-4 shadow-lg transition-all duration-300 ${colors[type] || colors.info}`;
  toast.style.transform = "translateX(100%)";
  toast.style.opacity = "0";
  
  toast.innerHTML = `
    ${icons[type] || icons.info}
    <p class="flex-1 text-sm font-medium">${escapeHtml(message)}</p>
    <button type="button" class="rounded px-1 hover:bg-black/5 dark:hover:bg-white/5 transition-colors" aria-label="Fermer">
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
    </button>
  `;
  
  const close = () => {
    toast.style.transform = "translateX(100%)";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  };
  
  toast.querySelector("button").addEventListener("click", close);
  getContainer().append(toast);
  
  requestAnimationFrame(() => {
    toast.style.transform = "translateX(0)";
    toast.style.opacity = "1";
  });
  
  if (duration) window.setTimeout(close, duration);
  return toast;
}

// Version améliorée
function showToastEnhanced(message, options = {}) {
  const {
    type = "info",
    duration = 4500,
    title = "",
    action = null,
  } = options;
  
  const colors = {
    success: "border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200",
    error: "border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-800 dark:bg-rose-950/50 dark:text-rose-200",
    warning: "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200",
    info: "border-blue-200 bg-blue-50 text-blue-900 dark:border-blue-800 dark:bg-blue-950/50 dark:text-blue-200",
  };
  
  const icons = {
    success: `<svg class="h-5 w-5 text-emerald-500 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    error: `<svg class="h-5 w-5 text-rose-500 dark:text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    warning: `<svg class="h-5 w-5 text-amber-500 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`,
    info: `<svg class="h-5 w-5 text-blue-500 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
  };
  
  const toast = document.createElement("div");
  toast.className = `flex items-start gap-3 rounded-xl border p-4 shadow-lg transition-all duration-300 ${colors[type] || colors.info}`;
  toast.style.transform = "translateX(100%)";
  toast.style.opacity = "0";
  
  let actionsHtml = "";
  if (action) {
    actionsHtml = `
      <button class="rounded-lg px-3 py-1 text-xs font-semibold ${action.class || 'bg-white/20 hover:bg-white/30 dark:bg-black/20 dark:hover:bg-black/30'} transition-colors" 
              onclick="(${action.callback.toString()})()">
        ${action.label}
      </button>
    `;
  }
  
  toast.innerHTML = `
    <div class="flex items-start gap-3 flex-1">
      ${icons[type] || icons.info}
      <div>
        ${title ? `<p class="text-sm font-bold">${escapeHtml(title)}</p>` : ''}
        <p class="text-sm font-medium ${title ? 'text-slate-600 dark:text-slate-300' : ''}">${escapeHtml(message)}</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      ${actionsHtml}
      <button type="button" class="rounded px-1 hover:bg-black/5 dark:hover:bg-white/5 transition-colors" aria-label="Fermer">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </div>
  `;
  
  const close = () => {
    toast.style.transform = "translateX(100%)";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  };
  
  toast.querySelector("button:last-child").addEventListener("click", close);
  getContainer().append(toast);
  
  requestAnimationFrame(() => {
    toast.style.transform = "translateX(0)";
    toast.style.opacity = "1";
  });
  
  if (duration) window.setTimeout(close, duration);
  return toast;
}

// Exporter un objet toast avec toutes les fonctions
export const toast = {
  show: showToast,
  success: (message, duration) => showToast(message, "success", duration),
  error: (message, duration) => showToast(message, "error", duration),
  warning: (message, duration) => showToast(message, "warning", duration),
  info: (message, duration) => showToast(message, "info", duration),
  enhanced: showToastEnhanced,
};

// Exports individuels pour compatibilité
export { showToast, showToastEnhanced };

// Export par défaut
export default toast;