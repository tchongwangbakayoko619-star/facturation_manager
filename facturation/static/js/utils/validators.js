export const isEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
export const isPositiveNumber = (value) => Number(value) > 0;

export function setFieldError(field, message = "") {
  const error = field.parentElement.querySelector("[data-client-error]");
  field.setAttribute("aria-invalid", String(Boolean(message)));
  if (error) error.remove();
  if (!message) return true;
  const feedback = document.createElement("p");
  feedback.dataset.clientError = "true";
  feedback.className = "mt-1 text-xs text-rose-600";
  feedback.textContent = message;
  field.insertAdjacentElement("afterend", feedback);
  return false;
}

export function validateRequiredFields(form) {
  return [...form.querySelectorAll("[required]")].every((field) =>
    setFieldError(field, field.value.trim() ? "" : "Ce champ est obligatoire."));
}
