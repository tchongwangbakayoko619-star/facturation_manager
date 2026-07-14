import { $$ } from "./utils/helpers.js";

export function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove("hidden");
  modal.classList.add("flex");
  document.body.classList.add("overflow-hidden");
  modal.querySelector("button, [href], input, select, textarea")?.focus();
}

export function closeModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add("hidden");
  modal.classList.remove("flex");
  if (!$$("[role='dialog']:not(.hidden)").length) document.body.classList.remove("overflow-hidden");
}

export function initModals() {
  $$('[data-modal-open]').forEach((button) => button.addEventListener("click", () => openModal(button.dataset.modalOpen)));
  $$('[data-modal-close]').forEach((button) => button.addEventListener("click", () => closeModal(button.dataset.modalClose)));
  $$("[role='dialog']").forEach((modal) => modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal(modal.id);
  }));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") $$("[role='dialog']:not(.hidden)").forEach((modal) => closeModal(modal.id));
  });
}
