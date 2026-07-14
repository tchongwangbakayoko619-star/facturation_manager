import { $, debounce } from "../utils/helpers.js";

export function initProductsPage() {
  const search = $("form[method='get'] input[type='search']");
  if (search) search.addEventListener("input", debounce(() => {
    if (!search.value || search.value.length >= 2) search.form.requestSubmit();
  }, 450));
  const image = $("input[type='file'][accept*='image']");
  image?.addEventListener("change", () => {
    const [file] = image.files;
    if (file && !file.type.startsWith("image/")) image.value = "";
  });
}
