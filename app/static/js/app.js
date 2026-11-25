(function () {
  const MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
  ];

  function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.remove(), 4500);
  }
  window.NutciToast = showToast;

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch((err) => {
        console.warn("Service Worker não registrado:", err);
      });
    });
  }

  let deferredPrompt = null;
  const installBtn = document.getElementById("install-pwa-btn");
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) installBtn.classList.remove("hidden");
  });

  if (installBtn) {
    installBtn.addEventListener("click", async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      installBtn.classList.add("hidden");
    });
  }

  function updateNetworkStatus() {
    const badge = document.getElementById("network-badge");
    const text = document.getElementById("network-text");
    if (!badge || !text) return;

    if (navigator.onLine) {
      badge.className = "badge badge-online";
      text.textContent = "Online";
      if (window.NutciOffline) window.NutciOffline.syncNow(true);
    } else {
      badge.className = "badge badge-offline";
      text.textContent = "Offline";
    }
  }

  window.addEventListener("online", updateNetworkStatus);
  window.addEventListener("offline", updateNetworkStatus);

  document.addEventListener("DOMContentLoaded", () => {
    updateNetworkStatus();
    if (window.NutciOffline) window.NutciOffline.updatePendingUI();

    const syncBtn = document.getElementById("sync-btn");
    const forceSyncBtn = document.getElementById("btn-force-sync");
    [syncBtn, forceSyncBtn].forEach((btn) => {
      if (btn) {
        btn.addEventListener("click", async () => {
          await window.NutciOffline.syncNow(true);
          if (window.location.pathname === "/historico") {
            window.location.reload();
          }
        });
      }
    });

    // Prévia da data por extenso
    const dataInput = document.getElementById("data_visita");
    const cidadeInput = document.getElementById("cidade");
    const previewDate = document.getElementById("preview-data-extenso");

    function updateDatePreview() {
      if (!dataInput || !cidadeInput || !previewDate) return;
      const cidade = cidadeInput.value.trim() || "Campina Grande - PB";
      if (!dataInput.value) {
        previewDate.textContent = `${cidade}, ______ de ___________________ de _______.`;
        return;
      }
      const [y, m, d] = dataInput.value.split("-").map(Number);
      const mesNome = MESES[(m || 1) - 1] || "";
      previewDate.textContent = `${cidade}, ${String(d).padStart(2, "0")} de ${mesNome} de ${y}.`;
    }

    if (dataInput && cidadeInput) {
      updateDatePreview();
      dataInput.addEventListener("change", updateDatePreview);
      cidadeInput.addEventListener("input", updateDatePreview);
    }

    // Seleção dos técnicos da equipe NUTCI (Guega, Jairo, João Paulo, Valdênio, Isaque)
    const tecnicoSelect = document.getElementById("tecnico_select");
    const tecnicoCustom = document.getElementById("tecnico_custom");
    const tecnicoHidden = document.getElementById("tecnico");
    const matriculaInput = document.getElementById("matricula");
    const previewNomeTecnico = document.getElementById("preview-nome-tecnico");
    const gestorInput = document.getElementById("gestor_nome");
    const previewNomeGestor = document.getElementById("preview-nome-gestor");

    function syncTecnicoFields() {
      if (!tecnicoSelect || !tecnicoHidden) return;
      const val = tecnicoSelect.value;
      if (val === "__outro__") {
        if (tecnicoCustom) tecnicoCustom.classList.remove("hidden");
        const nomeDigitado = tecnicoCustom ? tecnicoCustom.value.trim() : "";
        tecnicoHidden.value = nomeDigitado;
        if (previewNomeTecnico) previewNomeTecnico.textContent = nomeDigitado || " ";
      } else {
        if (tecnicoCustom) tecnicoCustom.classList.add("hidden");
        tecnicoHidden.value = val;
        if (previewNomeTecnico) previewNomeTecnico.textContent = val;
        const opt = tecnicoSelect.options[tecnicoSelect.selectedIndex];
        const matPadrao = opt ? opt.getAttribute("data-matricula") : "";
        if (matPadrao && matriculaInput && !matriculaInput.value) {
          matriculaInput.value = matPadrao;
        }
      }
    }

    if (tecnicoSelect) {
      syncTecnicoFields();
      tecnicoSelect.addEventListener("change", syncTecnicoFields);
      if (tecnicoCustom) {
        tecnicoCustom.addEventListener("input", syncTecnicoFields);
      }
    }

    if (gestorInput && previewNomeGestor) {
      gestorInput.addEventListener("input", () => {
        previewNomeGestor.textContent = gestorInput.value.trim() || " ";
      });
    }

    // Submissão do formulário
    const form = document.getElementById("relatorio-form");
    if (form) {
      const limparBtn = document.getElementById("btn-limpar-form");
      if (limparBtn) {
        limparBtn.addEventListener("click", () => {
          setTimeout(() => {
            syncTecnicoFields();
            updateDatePreview();
            if (previewNomeGestor) previewNomeGestor.textContent = " ";
          }, 15);
        });
      }

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        syncTecnicoFields();

        const submitBtn = document.getElementById("btn-salvar");
        submitBtn.disabled = true;
        submitBtn.textContent = "Salvando...";

        const formData = new FormData(form);
        const payload = {
          client_uuid: (crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()),
          escola_setor: formData.get("escola_setor"),
          data_visita: formData.get("data_visita"),
          cidade: formData.get("cidade"),
          endereco: formData.get("endereco"),
          motivo_chamado: formData.get("motivo_chamado"),
          tecnico: formData.get("tecnico"),
          matricula: formData.get("matricula"),
          gestor_nome: formData.get("gestor_nome"),
          problema_resolvido: formData.get("problema_resolvido"),
          tipo_assinatura: formData.get("tipo_assinatura"),
          descricao_atendimento: formData.get("descricao_atendimento"),
        };

        try {
          if (!navigator.onLine) {
            throw new Error("OFFLINE_MODE");
          }

          const response = await fetch("/api/relatorios", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });

          const result = await response.json();
          if (!response.ok || !result.ok) {
            showToast(result.error || "Verifique os campos obrigatórios.", "error");
            submitBtn.disabled = false;
            submitBtn.textContent = "Salvar e Preparar PDF / Impressão";
            return;
          }

          showToast(`Relatório ${result.relatorio.protocolo} salvo no Neon.tech!`, "success");
          window.location.href = result.redirect_url;
        } catch (err) {
          if (window.NutciOffline) {
            await window.NutciOffline.enqueueRelatorio(payload);
            await window.NutciOffline.updatePendingUI();
            showToast(
              "Sem conexão: relatório salvo no dispositivo e será enviado ao Neon.tech automaticamente.",
              "info"
            );
            form.reset();
            syncTecnicoFields();
            updateDatePreview();
          } else {
            showToast("Erro de rede ao salvar o relatório.", "error");
          }
          submitBtn.disabled = false;
          submitBtn.textContent = "Salvar e Preparar PDF / Impressão";
        }
      });
    }

    // Exclusão no histórico
    document.querySelectorAll(".btn-delete").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.getAttribute("data-id");
        const protocolo = btn.getAttribute("data-protocolo");
        if (!confirm(`Deseja realmente excluir o relatório ${protocolo}?`)) return;

        try {
          const resp = await fetch(`/api/relatorios/${id}`, { method: "DELETE" });
          if (resp.ok) {
            const row = document.getElementById(`row-${id}`);
            if (row) row.remove();
            showToast(`Relatório ${protocolo} excluído.`, "success");
          } else {
            showToast("Não foi possível excluir o relatório.", "error");
          }
        } catch (err) {
          showToast("Erro de conexão ao excluir.", "error");
        }
      });
    });
  });
})();
