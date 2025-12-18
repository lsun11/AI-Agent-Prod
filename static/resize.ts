// static/resize.ts

type Dir = "n" | "s" | "e" | "w" | "ne" | "nw" | "se" | "sw";

export interface ResizeOptions {
  minWidth?: number;   // default 320
  minHeight?: number;  // default 240
}

function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n));
}

export function makePanelResizable(panel: HTMLElement, opts: ResizeOptions = {}): void {
  const minW = opts.minWidth ?? 320;
  const minH = opts.minHeight ?? 240;

  // Create handles once
  const dirs: Dir[] = ["n","s","e","w","ne","nw","se","sw"];
  for (const d of dirs) {
    const h = document.createElement("div");
    h.className = `resize-handle ${d}`;
    h.dataset.dir = d;
    panel.appendChild(h);
  }

  let isResizing = false;
  let dir: Dir | null = null;

  let startX = 0;
  let startY = 0;

  // starting rect and positions
  let startLeft = 0;
  let startTop = 0;
  let startW = 0;
  let startH = 0;

  // Save/restore constraints
  let prevInset: string | null = null;
  let prevRight: string | null = null;
  let prevBottom: string | null = null;

  function beginResize(e: PointerEvent, d: Dir) {
    if (e.pointerType === "mouse" && e.button !== 0) return;

    isResizing = true;
    dir = d;

    panel.classList.add("is-resizing");

    const rect = panel.getBoundingClientRect();

    // Make it a floating fixed panel controlled by left/top/width/height
    panel.style.position = "fixed";

    // Clear inset constraints (your .gadget--expanded uses inset)
    prevInset = (panel.style as any).inset ?? "";
    prevRight = panel.style.right;
    prevBottom = panel.style.bottom;

    (panel.style as any).inset = "auto";
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
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
    } catch {}
  }

  function onMove(e: PointerEvent) {
    if (!isResizing || !dir) return;

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

    if (hasE) nextW = startW + dx;
    if (hasS) nextH = startH + dy;

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

  function endResize(e: PointerEvent) {
    if (!isResizing) return;
    isResizing = false;
    dir = null;

    panel.classList.remove("is-resizing");

    prevInset = prevRight = prevBottom = null;

    try {
      (e.target as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {}
  }

  // Delegate events from handles
  panel.addEventListener(
    "pointerdown",
    (e) => {
        if (!panel.classList.contains("gadget--expanded")) return;
      const t = e.target as HTMLElement | null;
      if (!t) return;
      const handle = t.closest(".resize-handle") as HTMLElement | null;
      if (!handle) return;
      const d = handle.dataset.dir as Dir | undefined;
      if (!d) return;
      beginResize(e as PointerEvent, d);
    },
    { passive: false },
  );



  window.addEventListener("pointermove", onMove, { passive: false });
  window.addEventListener("pointerup", endResize);
  window.addEventListener("pointercancel", endResize);
}
