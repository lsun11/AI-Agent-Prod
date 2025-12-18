// static/resize.ts
function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
}
export function makePanelResizable(panel, opts = {}) {
    var _a, _b;
    const minW = (_a = opts.minWidth) !== null && _a !== void 0 ? _a : 320;
    const minH = (_b = opts.minHeight) !== null && _b !== void 0 ? _b : 240;
    // Create handles once
    const dirs = ["n", "s", "e", "w", "ne", "nw", "se", "sw"];
    for (const d of dirs) {
        const h = document.createElement("div");
        h.className = `resize-handle ${d}`;
        h.dataset.dir = d;
        panel.appendChild(h);
    }
    let isResizing = false;
    let dir = null;
    let startX = 0;
    let startY = 0;
    // starting rect and positions
    let startLeft = 0;
    let startTop = 0;
    let startW = 0;
    let startH = 0;
    // Save/restore constraints
    let prevInset = null;
    let prevRight = null;
    let prevBottom = null;
    function beginResize(e, d) {
        var _a;
        if (e.pointerType === "mouse" && e.button !== 0)
            return;
        isResizing = true;
        dir = d;
        panel.classList.add("is-resizing");
        const rect = panel.getBoundingClientRect();
        // Make it a floating fixed panel controlled by left/top/width/height
        panel.style.position = "fixed";
        // Clear inset constraints (your .gadget--expanded uses inset)
        prevInset = (_a = panel.style.inset) !== null && _a !== void 0 ? _a : "";
        prevRight = panel.style.right;
        prevBottom = panel.style.bottom;
        panel.style.inset = "auto";
        panel.style.right = "auto";
        panel.style.bottom = "auto";
        // Lock explicit geometry
        panel.style.left = `${rect.left}px`;
        panel.style.top = `${rect.top}px`;
        panel.style.width = `${rect.width}px`;
        panel.style.height = `${rect.height}px`;
        startX = e.clientX;
        startY = e.clientY;
        startLeft = rect.left;
        startTop = rect.top;
        startW = rect.width;
        startH = rect.height;
        e.preventDefault();
        e.stopPropagation();
        try {
            e.target.setPointerCapture(e.pointerId);
        }
        catch (_b) { }
    }
    function onMove(e) {
        if (!isResizing || !dir)
            return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        // viewport bounds
        const maxW = window.innerWidth;
        const maxH = window.innerHeight;
        let nextLeft = startLeft;
        let nextTop = startTop;
        let nextW = startW;
        let nextH = startH;
        const hasN = dir.includes("n");
        const hasS = dir.includes("s");
        const hasW = dir.includes("w");
        const hasE = dir.includes("e");
        if (hasE)
            nextW = startW + dx;
        if (hasS)
            nextH = startH + dy;
        if (hasW) {
            nextW = startW - dx;
            nextLeft = startLeft + dx;
        }
        if (hasN) {
            nextH = startH - dy;
            nextTop = startTop + dy;
        }
        // enforce min sizes
        nextW = Math.max(minW, nextW);
        nextH = Math.max(minH, nextH);
        // clamp within viewport (keep top-left in bounds)
        nextLeft = clamp(nextLeft, 0, maxW - nextW);
        nextTop = clamp(nextTop, 0, maxH - nextH);
        // If clamped, also adjust size if needed so it still fits
        nextW = clamp(nextW, minW, maxW - nextLeft);
        nextH = clamp(nextH, minH, maxH - nextTop);
        panel.style.left = `${nextLeft}px`;
        panel.style.top = `${nextTop}px`;
        panel.style.width = `${nextW}px`;
        panel.style.height = `${nextH}px`;
        //     panel.style.setProperty("--gadget-exp-w", panel.style.width);
        // panel.style.setProperty("--gadget-exp-h", panel.style.height);
        //
        // localStorage.setItem(
        //   "ai-gadget-expanded-size",
        //   JSON.stringify({
        //     w: panel.style.getPropertyValue("--gadget-exp-w"),
        //     h: panel.style.getPropertyValue("--gadget-exp-h"),
        //   }),
        // );
        e.preventDefault();
    }
    function endResize(e) {
        if (!isResizing)
            return;
        isResizing = false;
        dir = null;
        panel.classList.remove("is-resizing");
        prevInset = prevRight = prevBottom = null;
        try {
            e.target.releasePointerCapture(e.pointerId);
        }
        catch (_a) { }
    }
    // Delegate events from handles
    panel.addEventListener("pointerdown", (e) => {
        if (!panel.classList.contains("gadget--expanded"))
            return;
        const t = e.target;
        if (!t)
            return;
        const handle = t.closest(".resize-handle");
        if (!handle)
            return;
        const d = handle.dataset.dir;
        if (!d)
            return;
        beginResize(e, d);
    }, { passive: false });
    window.addEventListener("pointermove", onMove, { passive: false });
    window.addEventListener("pointerup", endResize);
    window.addEventListener("pointercancel", endResize);
}
//# sourceMappingURL=resize.js.map