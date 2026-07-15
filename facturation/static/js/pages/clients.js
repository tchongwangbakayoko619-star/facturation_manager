import { $, $$, debounce, fetchJSON } from "../utils/helpers.js";
import { toast, showToastEnhanced } from "../toast.js";

export function initClientsPage() {
  // Vérifier qu'on est sur la page clients
  const page = $("#clients-page");
  if (!page) return;

  // ---- 1. RECHERCHE AVEC DEBOUNCE ----
  const search = $("form[method='get'] input[type='search']");
  if (search) {
    search.addEventListener("input", debounce(() => {
      if (search.value.length === 0 || search.value.length >= 2) {
        search.form.requestSubmit();
      }
    }, 450));
  }

  // ---- 2. CRÉATION D'UN CLIENT (via modal) ----
  const createForm = document.getElementById('client-form');
  if (createForm) {
    createForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(createForm);
      
      try {
        const response = await fetchJSON(createForm.action, {
          method: 'POST',
          body: formData,
        });
        
        if (response.success) {
          toast.success("👤 Client créé avec succès !", 3000);
          setTimeout(() => window.location.href = response.redirect || '/clients/', 1500);
        } else {
          const errors = Object.values(response.errors || {}).flat().join(', ');
          showToastEnhanced(
            "❌ Erreur de validation",
            errors || "Veuillez vérifier les champs du formulaire",
            "error",
            5000
          );
        }
      } catch (error) {
        toast.error("Erreur réseau - Veuillez réessayer", 5000);
      }
    });
  }

  // ---- 3. MODIFICATION D'UN CLIENT ----
  $$('.edit-client').forEach(button => {
    button.addEventListener('click', async () => {
      const clientId = button.dataset.clientId;
      // Ouvrir la modale avec les données du client
      openEditClientModal(clientId);
    });
  });

  // ---- 4. SUPPRESSION D'UN CLIENT ----
  $$('.delete-client').forEach(button => {
    button.addEventListener('click', async () => {
      const clientId = button.dataset.clientId;
      const clientName = button.dataset.clientName || 'ce client';
      
      // Confirmation stylisée
      if (!confirm(`⚠️ Voulez-vous vraiment supprimer "${clientName}" ?\nCette action est irréversible.`)) return;
      
      try {
        const response = await fetchJSON(`/clients/${clientId}/delete/`, {
          method: 'POST',
        });
        
        if (response.success) {
          toast.success(`🗑️ ${clientName} a été supprimé avec succès`, 3000);
          // Supprimer la ligne du tableau
          const row = button.closest('tr');
          if (row) {
            row.style.transition = 'opacity 0.3s';
            row.style.opacity = '0';
            setTimeout(() => row.remove(), 300);
          }
          // Mettre à jour le compteur
          updateClientCount();
        } else {
          toast.error(response.error || "Impossible de supprimer ce client", 5000);
        }
      } catch (error) {
        toast.error("Erreur lors de la suppression", 5000);
      }
    });
  });

  // ---- 5. EXPORT CSV ----
  const exportBtn = $('#export-csv');
  if (exportBtn) {
    exportBtn.addEventListener('click', async () => {
      try {
        toast.info("📊 Génération du fichier CSV...", 2000);
        const response = await fetch('/clients/export/csv/');
        
        if (response.ok) {
          toast.success("📁 CSV exporté avec succès !", 3000);
          window.location.href = '/clients/export/csv/';
        } else {
          toast.error("Erreur lors de l'export", 5000);
        }
      } catch (error) {
        toast.error("Erreur réseau", 5000);
      }
    });
  }

  // ---- 6. RECHERCHE AVANCÉE (filtres) ----
  const filters = $$('.client-filter');
  filters.forEach(filter => {
    filter.addEventListener('change', debounce(() => {
      // Soumettre le formulaire de filtrage
      const form = filter.closest('form');
      if (form) form.requestSubmit();
    }, 300));
  });

  // ---- 7. SELECTION MULTIPLE ----
  const selectAll = $('#select-all-clients');
  if (selectAll) {
    selectAll.addEventListener('change', () => {
      const checkboxes = $$('.client-checkbox');
      checkboxes.forEach(cb => cb.checked = selectAll.checked);
    });
  }

  // ---- 8. SUPPRESSION MULTIPLE ----
  const deleteSelected = $('#delete-selected');
  if (deleteSelected) {
    deleteSelected.addEventListener('click', async () => {
      const selected = $$('.client-checkbox:checked');
      if (selected.length === 0) {
        toast.warning("Aucun client sélectionné", 3000);
        return;
      }
      
      if (!confirm(`⚠️ Supprimer ${selected.length} client(s) ?`)) return;
      
      const ids = selected.map(cb => cb.dataset.clientId);
      try {
        const response = await fetchJSON('/clients/bulk-delete/', {
          method: 'POST',
          body: JSON.stringify({ ids }),
        });
        
        if (response.success) {
          toast.success(`🗑️ ${selected.length} client(s) supprimé(s) avec succès`, 3000);
          setTimeout(() => window.location.reload(), 1500);
        } else {
          toast.error(response.error || "Erreur lors de la suppression", 5000);
        }
      } catch (error) {
        toast.error("Erreur réseau", 5000);
      }
    });
  }

  // ---- 9. NOTIFICATION DE BIENVENUE (une seule fois) ----
  if (!sessionStorage.getItem('clients_page_visited')) {
    sessionStorage.setItem('clients_page_visited', 'true');
    // Ne pas afficher si d'autres toasts sont présents
    setTimeout(() => {
      toast.info("💡 Utilisez la barre de recherche pour filtrer vos clients", 4000);
    }, 1000);
  }
}

// ---- FONCTIONS UTILITAIRES ----

// Mettre à jour le compteur de clients
function updateClientCount() {
  const counter = document.getElementById('client-count');
  if (counter) {
    const current = parseInt(counter.textContent) || 0;
    counter.textContent = current - 1;
  }
}

// Ouvrir la modale d'édition
async function openEditClientModal(clientId) {
  try {
    const response = await fetch(`/clients/${clientId}/edit/`);
    const html = await response.text();
    
    const modal = document.getElementById('edit-client-modal');
    if (modal) {
      modal.innerHTML = html;
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
      
      // Re-initialiser le formulaire après chargement
      const form = modal.querySelector('form');
      if (form) {
        form.addEventListener('submit', handleEditSubmit);
      }
    }
  } catch (error) {
    toast.error("Impossible de charger les données du client", 5000);
  }
}

// Gérer la soumission du formulaire d'édition
async function handleEditSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  
  try {
    const response = await fetchJSON(form.action, {
      method: 'POST',
      body: formData,
    });
    
    if (response.success) {
      toast.success("👤 Client modifié avec succès", 3000);
      setTimeout(() => window.location.reload(), 1500);
    } else {
      toast.error(response.error || "Erreur de modification", 5000);
    }
  } catch (error) {
    toast.error("Erreur réseau", 5000);
  }
}

// ---- FIN DE LA PAGE CLIENTS ----