import { $, debounce } from "../utils/helpers.js";

export function initClientsPage() {
  const search = $("form[method='get'] input[type='search']");
  if (!search) return;
  search.addEventListener("input", debounce(() => {
    if (search.value.length === 0 || search.value.length >= 2) search.form.requestSubmit();
  }, 450));
}
