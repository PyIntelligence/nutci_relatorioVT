(function () {
  const DB_NAME = "nutci_offline_db";
  const STORE_NAME = "pending_relatorios";
  const DB_VERSION = 1;

  function openDB() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: "client_uuid" });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function enqueueRelatorio(item) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).put(item);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async function getAllPending() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readonly");
      const req = tx.objectStore(STORE_NAME).getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  async function removePending(clientUuids) {
    if (!clientUuids.length) return;
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);
      clientUuids.forEach((id) => store.delete(id));
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async function updatePendingUI() {
    const items = await getAllPending();
    const count = items.length;
    const syncBtn = document.getElementById("sync-btn");
    const countSpan = document.getElementById("pending-count");
    const panel = document.getElementById("offline-queue-panel");
    const summary = document.getElementById("offline-queue-summary");

    if (countSpan) countSpan.textContent = String(count);
    if (syncBtn) syncBtn.classList.toggle("hidden", count === 0);
    if (panel && summary) {
      panel.classList.toggle("hidden", count === 0);
      summary.textContent = `${count} relatório(s) pendente(s)`;
    }
  }

  async function syncNow(notify = true) {
    if (!navigator.onLine) return;
    const items = await getAllPending();
    if (!items.length) return;

    try {
      const resp = await fetch("/api/relatorios/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items }),
      });
      if (!resp.ok) return;
      const data = await resp.json();
      const syncedIds = (data.synced || []).map((s) => s.client_uuid).filter(Boolean);
      if (syncedIds.length) {
        await removePending(syncedIds);
        await updatePendingUI();
        if (notify && window.NutciToast) {
          window.NutciToast(`${syncedIds.length} relatório(s) sincronizado(s) com o Neon.tech!`, "success");
        }
      }
    } catch (err) {
      console.warn("Falha na sincronização offline:", err);
    }
  }

  window.NutciOffline = {
    enqueueRelatorio,
    getAllPending,
    updatePendingUI,
    syncNow,
  };
})();
