// static/drag.ts
/**
 * Make a panel draggable using the given handle element.
 *
 * Stable drag:
 * - preserves grab offset (no jump)
 * - freezes size during drag (no jitter from transitions/resizes)
 * - disables transitions/animations while dragging (CSS class)
 */
export function makePanelDraggable2(panel, handle) {
    let isDragging = false;
    let grabOffsetX = 0;
    let grabOffsetY = 0;
    let panelW = 0;
    let panelH = 0;
    let maxLeft = 0;
    let maxTop = 0;
    let prevUserSelect = null;
    // Ensure fixed positioning (you already do this)
    if (!panel.style.position)
        panel.style.position = "fixed";
    const onPointerDown = (event) => {
        // Only left click for mouse; allow touch/pen
        if (event.pointerType === "mouse" && event.button !== 0)
            return;
        // If you click inside a button/link/input in the handle, don't start drag
        const target = event.target;
        if (target && target.closest("button, a, input, select, textarea"))
            return;
        const rect = panel.getBoundingClientRect();
        // compute grab offset so cursor doesn't "jump" to top-left
        grabOffsetX = event.clientX - rect.left;
        grabOffsetY = event.clientY - rect.top;
        // freeze dimensions for the duration of the drag (prevents jitter)
        panelW = rect.width;
        panelH = rect.height;
        // clamp boundaries (viewport)
        maxLeft = Math.max(0, window.innerWidth - panelW);
        maxTop = Math.max(0, window.innerHeight - panelH);
        // set explicit left/top once, so future rects are consistent
        panel.style.left = `${rect.left}px`;
        panel.style.top = `${rect.top}px`;
        // lock size while dragging (avoid layout/transition jitter)
        panel.style.width = `${panelW}px`;
        panel.style.height = `${panelH}px`;
        // add dragging class (turn off transitions/animations in CSS)
        panel.classList.add("is-dragging");
        isDragging = true;
        // prevent selection / scrolling during drag
        prevUserSelect = document.body.style.userSelect;
        document.body.style.userSelect = "none";
        event.preventDefault();
        try {
            handle.setPointerCapture(event.pointerId);
        }
        catch (_a) {
            // ignore
        }
    };
    const onPointerMove = (event) => {
        if (!isDragging)
            return;
        let nextLeft = event.clientX - grabOffsetX;
        let nextTop = event.clientY - grabOffsetY;
        // clamp inside viewport
        if (nextLeft < 0)
            nextLeft = 0;
        if (nextTop < 0)
            nextTop = 0;
        if (nextLeft > maxLeft)
            nextLeft = maxLeft;
        if (nextTop > maxTop)
            nextTop = maxTop;
        panel.style.left = `${nextLeft}px`;
        panel.style.top = `${nextTop}px`;
    };
    const endDrag = (event) => {
        if (!isDragging)
            return;
        isDragging = false;
        panel.classList.remove("is-dragging");
        // unfreeze size after drag
        panel.style.width = "";
        panel.style.height = "";
        if (prevUserSelect !== null) {
            document.body.style.userSelect = prevUserSelect;
            prevUserSelect = null;
        }
        if (event) {
            try {
                handle.releasePointerCapture(event.pointerId);
            }
            catch (_a) {
                // ignore
            }
        }
    };
    handle.addEventListener("pointerdown", onPointerDown, { passive: false });
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", (e) => endDrag(e));
    window.addEventListener("pointercancel", () => endDrag());
}
//# sourceMappingURL=drag2.js.map