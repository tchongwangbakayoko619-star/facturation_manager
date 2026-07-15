import { $ } from "../utils/helpers.js";

export function initDashboardPage() {
  // Les graphiques sont initialisés par le script Chart.js du tableau de bord.
  // Ce module est réservé aux interactions supplémentaires de cette page.

  highlightOverdueCard();
}

function highlightOverdueCard() {
  const overdueCard = $("[data-stat='overdue']");
  if (!overdueCard) return;

  const countElement = overdueCard.querySelector("strong");
  const count = Number(countElement?.textContent.trim() || 0);

  if (count > 0) {
    overdueCard.classList.add("ring-2", "ring-rose-300", "animate-pulse");
    window.setTimeout(() => {
      overdueCard.classList.remove("animate-pulse");
    }, 2000);
  }
}