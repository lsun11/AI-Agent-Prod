// static/drag.ts
/**
 * Make a panel draggable using the given handle element.
 *
 * - panel: the element that actually moves
 * - handle: the element the user drags (e.g. header/title bar)
 */
export function makePanelDraggable(panel, handle) {
    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let startLeft = 0;
    let startTop = 0;
    let prevUserSelect = null;
    // Ensure we can move it freely
    if (!panel.style.position) {
        panel.style.position = "fixed";
    }
    const onPointerDown = (event) => {
        isDragging = true;
        const rect = panel.getBoundingClientRect();
        startLeft = rect.left;
        startTop = rect.top;
        startX = event.clientX;
        startY = event.clientY;
        // Improve UX: prevent text selection while dragging
        prevUserSelect = document.body.style.userSelect;
        document.body.style.userSelect = "none";
        handle.setPointerCapture(event.pointerId);
    };
    const onPointerMove = (event) => {
        if (!isDragging)
            return;
        const dx = event.clientX - startX;
        const dy = event.clientY - startY;
        let nextLeft = startLeft + dx;
        let nextTop = startTop + dy;
        // Clamp inside viewport
        const panelRect = panel.getBoundingClientRect();
        const maxLeft = window.innerWidth - panelRect.width;
        const maxTop = window.innerHeight - panelRect.height;
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
    const onPointerUp = (event) => {
        if (!isDragging)
            return;
        isDragging = false;
        if (prevUserSelect !== null) {
            document.body.style.userSelect = prevUserSelect;
            prevUserSelect = null;
        }
        try {
            handle.releasePointerCapture(event.pointerId);
        }
        catch (_a) {
            // ignore if capture wasn't set
        }
    };
    handle.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
}
//# sourceMappingURL=drag.js.map