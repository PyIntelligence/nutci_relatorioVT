(function () {
  const pads = {};

  function setupPad(name, canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let drawing = false;
    let hasInk = false;

    ctx.lineWidth = 2.1;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#0a2e5c";

    function getPos(evt) {
      const rect = canvas.getBoundingClientRect();
      const clientX = evt.touches ? evt.touches[0].clientX : evt.clientX;
      const clientY = evt.touches ? evt.touches[0].clientY : evt.clientY;
      return {
        x: ((clientX - rect.left) / rect.width) * canvas.width,
        y: ((clientY - rect.top) / rect.height) * canvas.height,
      };
    }

    function startDraw(evt) {
      evt.preventDefault();
      drawing = true;
      hasInk = true;
      const pos = getPos(evt);
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
    }

    function moveDraw(evt) {
      if (!drawing) return;
      evt.preventDefault();
      const pos = getPos(evt);
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
    }

    function endDraw() {
      drawing = false;
    }

    canvas.addEventListener("mousedown", startDraw);
    canvas.addEventListener("mousemove", moveDraw);
    window.addEventListener("mouseup", endDraw);

    canvas.addEventListener("touchstart", startDraw, { passive: false });
    canvas.addEventListener("touchmove", moveDraw, { passive: false });
    canvas.addEventListener("touchend", endDraw);

    pads[name] = {
      clear() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        hasInk = false;
      },
      toDataURL() {
        return hasInk ? canvas.toDataURL("image/png") : null;
      },
    };
  }

  setupPad("tecnico", "canvas-tecnico");
  setupPad("gestor", "canvas-gestor");

  document.querySelectorAll(".btn-clear-sig").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-target");
      if (pads[target]) pads[target].clear();
    });
  });

  window.NutciSignatures = {
    getTecnico: () => (pads.tecnico ? pads.tecnico.toDataURL() : null),
    getGestor: () => (pads.gestor ? pads.gestor.toDataURL() : null),
    clearAll: () => {
      if (pads.tecnico) pads.tecnico.clear();
      if (pads.gestor) pads.gestor.clear();
    },
  };
})();
