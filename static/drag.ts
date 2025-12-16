// static/drag.ts

/**
 * Make a panel draggable using the given handle element.
 *
 * - panel: the element that actually moves
 * - handle: the element the user drags (e.g. header/title bar)
 */
// static/drag.ts

/**
 * Make a panel draggable using the given handle element.
 *
 * If the panel is inside a transformed container (like your gadget),
 * position: fixed will behave weird. We therefore:
 * - find the closest .gadget--expanded (if any)
 * - clamp movement inside that container
 * - use position: absolute (relative to the container) when expanded
 * - fall back to viewport clamp otherwise
 */
export function makePanelDraggable(panel: HTMLElement, handle: HTMLElement): void {
  let isDragging = false;

  // pointer start
  let startClientX = 0;
  let startClientY = 0;

  // panel start (in boundary coords)
  let startLeft = 0;
  let startTop = 0;

  // boundary at drag start
  let boundaryEl: HTMLElement | null = null;
  let boundaryRect: DOMRect | null = null;

  let prevUserSelect: string | null = null;

  function findBoundary(): HTMLElement | null {
    // Clamp to the expanded gadget if present; otherwise viewport.
    return panel.closest(".gadget--expanded") as HTMLElement | null;
  }

  function getPanelLeftTopInBoundary(panelRect: DOMRect, boundRect: DOMRect | null) {
    if (!boundRect) {
      // viewport coords
      return { left: panelRect.left, top: panelRect.top };
    }
    // coords relative to boundary box
    return { left: panelRect.left - boundRect.left, top: panelRect.top - boundRect.top };
  }

  function setPanelPositioningForBoundary(bound: HTMLElement | null) {
    if (bound) {
      // Make boundary a positioning context
      const cs = window.getComputedStyle(bound);
      if (cs.position === "static") bound.style.position = "relative";

      // Use absolute so we are inside the gadget box (NOT viewport)
      panel.style.position = "absolute";
    } else {
      // fallback: old behavior
      panel.style.position = "fixed";
    }
  }

  const onPointerDown = (event: PointerEvent) => {
    // Only left click / primary touch
    if (event.button !== 0) return;

    isDragging = true;

    boundaryEl = findBoundary();
    boundaryRect = boundaryEl ? boundaryEl.getBoundingClientRect() : null;

    setPanelPositioningForBoundary(boundaryEl);

    const panelRect = panel.getBoundingClientRect();
    const start = getPanelLeftTopInBoundary(panelRect, boundaryRect);

    startLeft = start.left;
    startTop = start.top;

    startClientX = event.clientX;
    startClientY = event.clientY;

    // prevent selection while dragging
    prevUserSelect = document.body.style.userSelect;
    document.body.style.userSelect = "none";

    handle.setPointerCapture(event.pointerId);
  };

  const onPointerMove = (event: PointerEvent) => {
    if (!isDragging) return;

    const dx = event.clientX - startClientX;
    const dy = event.clientY - startClientY;

    let nextLeft = startLeft + dx;
    let nextTop = startTop + dy;

    // Clamp size using CURRENT rect sizes (stable)
    const panelRect = panel.getBoundingClientRect();

    if (boundaryRect) {
      const maxLeft = boundaryRect.width - panelRect.width;
      const maxTop = boundaryRect.height - panelRect.height;

      if (nextLeft < 0) nextLeft = 0;
      if (nextTop < 0) nextTop = 0;
      if (nextLeft > maxLeft) nextLeft = maxLeft;
      if (nextTop > maxTop) nextTop = maxTop;
    } else {
      // viewport clamp
      const maxLeft = window.innerWidth - panelRect.width;
      const maxTop = window.innerHeight - panelRect.height;

      if (nextLeft < 0) nextLeft = 0;
      if (nextTop < 0) nextTop = 0;
      if (nextLeft > maxLeft) nextLeft = maxLeft;
      if (nextTop > maxTop) nextTop = maxTop;
    }

    panel.style.left = `${nextLeft}px`;
    panel.style.top = `${nextTop}px`;
  };

  const onPointerUp = (event: PointerEvent) => {
    if (!isDragging) return;
    isDragging = false;

    if (prevUserSelect !== null) {
      document.body.style.userSelect = prevUserSelect;
      prevUserSelect = null;
    }

    try {
      handle.releasePointerCapture(event.pointerId);
    } catch {
      // ignore
    }

    boundaryEl = null;
    boundaryRect = null;
  };

  handle.addEventListener("pointerdown", onPointerDown);
  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerup", onPointerUp);
}

