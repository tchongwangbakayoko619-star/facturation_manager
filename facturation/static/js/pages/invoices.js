import { $, $$, fetchJSON } from "../utils/helpers.js";
import { showToast } from "../toast.js";

function bindProductSelect(select, productUrlTemplate) {
  if (!select || select.dataset.bound) return;
  select.dataset.bound = "true";
  select.addEventListener("change", async () => {
    if (!select.value) return;
    const row = select.closest("tr");
    const description = $("[data-line-description]", row);
    const price = $("[data-line-price]", row);
    try {
      const productUrl = productUrlTemplate.replace(/0\/json\/?$/, `${select.value}/json/`);
      const product = await fetchJSON(productUrl);
      if (description && !description.value) description.value = product.description;
      if (price) price.value = product.prix_unitaire;
      if (product.en_rupture) showToast("Ce produit est en rupture de stock.", "warning");
    } catch (error) {
      showToast("Impossible de récupérer les informations du produit.", "error");
    }
  });
}

export function initInvoicesPage() {
  const form = $("[data-invoice-form]");
  if (!form) return;
  const rows = $("[data-invoice-lines]", form);
  const addButton = $("[data-add-invoice-line]", form);
  const addUrl = form.dataset.addLineUrl;
  const productUrl = form.dataset.productUrl;
  $$("[data-product-select]", rows).forEach((select) => bindProductSelect(select, productUrl));

  addButton?.addEventListener("click", async () => {
    const totalInput = $("[name$='TOTAL_FORMS']", form);
    const index = Number(totalInput?.value);
    if (!Number.isInteger(index) || !addUrl) return;
    addButton.disabled = true;
    try {
      const response = await fetch(`${addUrl}?index=${index}`, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      if (!response.ok) throw new Error("Échec de l’ajout");
      rows.insertAdjacentHTML("beforeend", await response.text());
      totalInput.value = index + 1;
      bindProductSelect($("[data-product-select]", rows.lastElementChild), productUrl);
      $("[data-product-select]", rows.lastElementChild)?.focus();
    } catch (error) {
      showToast("Impossible d’ajouter une ligne de facture.", "error");
    } finally {
      addButton.disabled = false;
    }
  });
}
