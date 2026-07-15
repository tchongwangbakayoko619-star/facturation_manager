import { $, $$ } from "./utils/helpers.js";

export function initNavbar() {
  const sidebar = $("#sidebar");
  const backdrop = $("#sidebar-backdrop");
  const setSidebar = (open) => {
    sidebar?.classList.toggle("-translate-x-full", !open);
    backdrop?.classList.toggle("hidden", !open);
    document.body.classList.toggle("overflow-hidden", open);
  };
  $("#sidebar-toggle")?.addEventListener("click", () => setSidebar(sidebar?.classList.contains("-translate-x-full")));
  backdrop?.addEventListener("click", () => setSidebar(false));
  $$("#sidebar a").forEach((link) => link.addEventListener("click", () => setSidebar(false)));

  const themeToggle = $("#theme-toggle");
  const themeMenu = $("#theme-menu");
  const applyTheme = (theme) => {
    const dark = theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.classList.toggle("dark", dark);
    if (theme === "system") localStorage.removeItem("color-theme");
    else localStorage.setItem("color-theme", theme);
  };
  themeToggle?.addEventListener("click", () => {
    const isOpen = !themeMenu?.classList.contains("hidden");
    themeMenu?.classList.toggle("hidden", isOpen);
    themeToggle.setAttribute("aria-expanded", String(!isOpen));
  });
  $$('[data-theme-value]').forEach((button) => button.addEventListener("click", () => {
    applyTheme(button.dataset.themeValue);
    themeMenu?.classList.add("hidden");
    themeToggle?.setAttribute("aria-expanded", "false");
  }));
  document.addEventListener("click", (event) => {
    if (!event.target.closest("#theme-toggle, #theme-menu")) {
      themeMenu?.classList.add("hidden");
      themeToggle?.setAttribute("aria-expanded", "false");
    }
  });

  // --- Plein écran ---
  const FULLSCREEN_KEY = "wasFullscreen";

  $("#fullscreen-toggle")?.addEventListener("click", async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
        sessionStorage.removeItem(FULLSCREEN_KEY);
      } else {
        await document.documentElement.requestFullscreen();
        sessionStorage.setItem(FULLSCREEN_KEY, "1");
      }
    } catch {
      // Le navigateur ou l'intégration actuelle peut interdire le plein écran.
    }
  });

  // Si on était en plein écran avant un changement de page (navigation
  // classique de la sidebar, qui recharge le document), on tente de le
  // restaurer automatiquement. Certains navigateurs (notamment Firefox)
  // refusent requestFullscreen() hors d'un geste utilisateur direct : dans
  // ce cas l'appel échoue silencieusement et on nettoie le flag pour éviter
  // de retenter indéfiniment sur les pages suivantes.
  if (sessionStorage.getItem(FULLSCREEN_KEY) === "1") {
    document.documentElement.requestFullscreen().catch(() => {
      sessionStorage.removeItem(FULLSCREEN_KEY);
    });
  }

  // Garde le flag synchronisé si l'utilisateur quitte le plein écran
  // manuellement (touche Échap, ou bouton natif du navigateur).
  document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement) {
      sessionStorage.removeItem(FULLSCREEN_KEY);
    } else {
      sessionStorage.setItem(FULLSCREEN_KEY, "1");
    }
  });

  $$('[data-alert-close]').forEach((button) => button.addEventListener("click", () => button.closest("[role='alert']")?.remove()));
}