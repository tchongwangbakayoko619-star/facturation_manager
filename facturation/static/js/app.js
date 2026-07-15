  import { initModals } from "./modal.js";
  import { initNavbar } from "./navbar.js";
  import { initClientsPage } from "./pages/clients.js";
  import { initDashboardPage } from "./pages/dashboard.js";
  import { initInvoicesPage } from "./pages/invoices.js";
  import { initProductsPage } from "./pages/products.js";

  document.addEventListener("DOMContentLoaded", () => {
    initNavbar();
    initModals();
    initClientsPage();
    initProductsPage();
    initInvoicesPage();
    initDashboardPage();
  });
