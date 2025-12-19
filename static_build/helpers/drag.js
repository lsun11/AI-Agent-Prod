// static/drag.ts
export function makePanelDraggable(panel, handle, options) {
    var _a, _b, _c, _d, _e;
    const mode = options.mode;
    const boundarySelector = (_a = options.boundarySelector) !== null && _a !== void 0 ? _a : ".gadget--expanded";
    const dragThresholdPx = (_b = options.dragThresholdPx) !== null && _b !== void 0 ? _b : 6;
    const inertiaEnabled = (_c = options.inertia) !== null && _c !== void 0 ? _c : true;
    const inertiaFriction = (_d = options.inertiaFriction) !== null && _d !== void 0 ? _d : 0.92;
    const inertiaStopSpeed = (_e = options.inertiaStopSpeed) !== null && _e !== void 0 ? _e : 0.02;
    let isDragging = false;
    // pointer start
    let startClientX = 0;
    let startClientY = 0;
    // panel start position (in boundary coords or viewport coords depending on mode)
    let startLeft = 0;
    let startTop = 0;
    // grab-offset mode specific
    let grabOffsetX = 0;
    let grabOffsetY = 0;
    let panelW = 0;
    let panelH = 0;
    let maxLeft = 0;
    let maxTop = 0;
    // boundary mode specific
    let boundaryEl = null;
    let boundaryRect = null;
    // click suppression
    let moved = false;
    let suppressNextClick = false;
    // velocity tracking (for inertia)
    let lastMoveT = 0;
    let lastMoveX = 0;
    let lastMoveY = 0;
    let vx = 0; // px/ms
    let vy = 0; // px/ms
    let inertiaRaf = null;
    let prevUserSelect = null;
    // ---- helpers ----
    function stopInertia() {
        if (inertiaRaf !== null) {
            cancelAnimationFrame(inertiaRaf);
            inertiaRaf = null;
        }
    }
    function clamp(n, min, max) {
        return Math.max(min, Math.min(max, n));
    }
    function findBoundary() {
        return panel.closest(boundarySelector);
    }
    function setPanelPositioningForBoundary(bound) {
        if (bound) {
            const cs = window.getComputedStyle(bound);
            if (cs.position === "static")
                bound.style.position = "relative";
            // inside boundary box
            panel.style.position = "absolute";
        }
        else {
            // viewport
            panel.style.position = "fixed";
        }
    }
    function getPanelLeftTopInBoundary(panelRect, boundRect) {
        if (!boundRect)
            return { left: panelRect.left, top: panelRect.top };
        return { left: panelRect.left - boundRect.left, top: panelRect.top - boundRect.top };
    }
    function computeBoundsForGrabOffset() {
        // viewport clamp
        maxLeft = Math.max(0, window.innerWidth - panelW);
        maxTop = Math.max(0, window.innerHeight - panelH);
    }
    function computeBoundsForBoundaryMode(panelRect) {
        if (boundaryRect) {
            return {
                maxL: Math.max(0, boundaryRect.width - panelRect.width),
                maxT: Math.max(0, boundaryRect.height - panelRect.height),
            };
        }
        return {
            maxL: Math.max(0, window.innerWidth - panelRect.width),
            maxT: Math.max(0, window.innerHeight - panelRect.height),
        };
    }
    function updateVelocity(event) {
        const now = performance.now();
        if (lastMoveT > 0) {
            const dt = now - lastMoveT;
            if (dt > 0) {
                const dx = event.clientX - lastMoveX;
                const dy = event.clientY - lastMoveY;
                vx = dx / dt;
                vy = dy / dt;
            }
        }
        lastMoveT = now;
        lastMoveX = event.clientX;
        lastMoveY = event.clientY;
    }
    function startInertiaIfNeeded() {
        if (mode !== "grab-offset")
            return;
        if (!inertiaEnabled)
            return;
        if (!moved)
            return;
        // If velocity is tiny, don't animate
        if (Math.abs(vx) < inertiaStopSpeed && Math.abs(vy) < inertiaStopSpeed)
            return;
        stopInertia();
        let x = parseFloat(panel.style.left || "0");
        let y = parseFloat(panel.style.top || "0");
        let lastT = performance.now();
        const tick = () => {
            const now = performance.now();
            const dt = now - lastT;
            lastT = now;
            // integrate
            x += vx * dt;
            y += vy * dt;
            // friction
            vx *= inertiaFriction;
            vy *= inertiaFriction;
            // clamp
            x = clamp(x, 0, maxLeft);
            y = clamp(y, 0, maxTop);
            panel.style.left = `${x}px`;
            panel.style.top = `${y}px`;
            const done = Math.abs(vx) < inertiaStopSpeed &&
                Math.abs(vy) < inertiaStopSpeed;
            if (!done) {
                inertiaRaf = requestAnimationFrame(tick);
            }
            else {
                inertiaRaf = null;
            }
        };
        inertiaRaf = requestAnimationFrame(tick);
    }
    // Suppress click that happens after a drag (this prevents gadget header click-open)
    handle.addEventListener("click", (e) => {
        if (!suppressNextClick)
            return;
        suppressNextClick = false;
        e.preventDefault();
        e.stopPropagation();
    }, true);
    // ---- pointer handlers ----
    const onPointerDown = (event) => {
        // Only left click for mouse; allow touch/pen
        if (event.pointerType === "mouse" && event.button !== 0)
            return;
        // If you click on interactive controls inside the handle, don't drag
        const target = event.target;
        if (target && target.closest("button, a, input, select, textarea"))
            return;
        stopInertia();
        isDragging = true;
        moved = false;
        suppressNextClick = false;
        startClientX = event.clientX;
        startClientY = event.clientY;
        // prevent selection while dragging
        prevUserSelect = document.body.style.userSelect;
        document.body.style.userSelect = "none";
        const rect = panel.getBoundingClientRect();
        if (mode === "boundary") {
            boundaryEl = findBoundary();
            boundaryRect = boundaryEl ? boundaryEl.getBoundingClientRect() : null;
            setPanelPositioningForBoundary(boundaryEl);
            const start = getPanelLeftTopInBoundary(rect, boundaryRect);
            startLeft = start.left;
            startTop = start.top;
        }
        else {
            // grab-offset mode: compute offset so cursor doesn't jump
            panel.classList.add("is-dragging");
            // Clear inset-based constraints (your .gadget--expanded uses inset)
            panel.style.removeProperty("inset");
            panel.style.right = "auto";
            panel.style.bottom = "auto";
            // Lock size to prevent stretching while moving
            panel.style.width = `${rect.width}px`;
            panel.style.height = `${rect.height}px`;
            // ensure fixed
            panel.style.position = "fixed";
            // IMPORTANT: set explicit left/top so subsequent moves are stable
            panel.style.left = `${rect.left}px`;
            panel.style.top = `${rect.top}px`;
            // Use the initial rect width/height only for bounds calculations (no resizing lock)
            panelW = rect.width;
            panelH = rect.height;
            grabOffsetX = event.clientX - rect.left;
            grabOffsetY = event.clientY - rect.top;
            // bounds based on current size
            panelW = rect.width;
            panelH = rect.height;
            computeBoundsForGrabOffset();
        }
        // init velocity tracking
        lastMoveT = 0;
        lastMoveX = event.clientX;
        lastMoveY = event.clientY;
        vx = 0;
        vy = 0;
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
        const dxFromStart = event.clientX - startClientX;
        const dyFromStart = event.clientY - startClientY;
        if (!moved && (Math.abs(dxFromStart) > dragThresholdPx || Math.abs(dyFromStart) > dragThresholdPx)) {
            moved = true;
        }
        if (mode === "boundary") {
            const dx = event.clientX - startClientX;
            const dy = event.clientY - startClientY;
            let nextLeft = startLeft + dx;
            let nextTop = startTop + dy;
            const panelRect = panel.getBoundingClientRect();
            const { maxL, maxT } = computeBoundsForBoundaryMode(panelRect);
            nextLeft = clamp(nextLeft, 0, maxL);
            nextTop = clamp(nextTop, 0, maxT);
            panel.style.left = `${nextLeft}px`;
            panel.style.top = `${nextTop}px`;
        }
        else {
            // grab-offset
            updateVelocity(event);
            let nextLeft = event.clientX - grabOffsetX;
            let nextTop = event.clientY - grabOffsetY;
            nextLeft = clamp(nextLeft, 0, maxLeft);
            nextTop = clamp(nextTop, 0, maxTop);
            panel.style.left = `${nextLeft}px`;
            panel.style.top = `${nextTop}px`;
        }
    };
    const onPointerUp = (event) => {
        if (!isDragging)
            return;
        isDragging = false;
        // If we moved, suppress the click that would otherwise toggle the gadget
        if (moved)
            suppressNextClick = true;
        if (prevUserSelect !== null) {
            document.body.style.userSelect = prevUserSelect;
            prevUserSelect = null;
        }
        try {
            handle.releasePointerCapture(event.pointerId);
        }
        catch (_a) {
            // ignore
        }
        if (mode === "boundary") {
            boundaryEl = null;
            boundaryRect = null;
        }
        else {
            panel.classList.remove("is-dragging");
            startInertiaIfNeeded();
        }
    };
    handle.addEventListener("pointerdown", onPointerDown, { passive: false });
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    window.addEventListener("pointercancel", onPointerUp);
    // keep grab-offset bounds correct on resize
    window.addEventListener("resize", () => {
        if (mode === "grab-offset") {
            // recalc using current size
            const rect = panel.getBoundingClientRect();
            panelW = rect.width;
            panelH = rect.height;
            computeBoundsForGrabOffset();
        }
    });
}
//# sourceMappingURL=drag.js.map