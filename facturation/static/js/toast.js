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

export function showToast(message, type = "info", duration = 4500) {
  const colors = {
    success: "border-emerald-200 bg-emerald-50 text-emerald-900",
    error: "border-rose-200 bg-rose-50 text-rose-900",
    warning: "border-amber-200 bg-amber-50 text-amber-900",
    info: "border-blue-200 bg-blue-50 text-blue-900",
  };
  const toast = document.createElement("div");
  toast.className = `flex items-start gap-3 rounded-xl border p-4 shadow-lg ${colors[type] || colors.info}`;
  toast.innerHTML = `<p class="flex-1 text-sm font-medium">${escapeHtml(message)}</p><button type="button" class="rounded px-1" aria-label="Fermer">×</button>`;
  const close = () => toast.remove();
  toast.querySelector("button").addEventListener("click", close);
  getContainer().append(toast);
  if (duration) window.setTimeout(close, duration);
  return toast;
}
