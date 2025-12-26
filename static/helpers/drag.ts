// static/helpers/drag.ts

type DragMode = "boundary" | "grab-offset";

export interface DragOptions {
    mode: DragMode;

    /**
     * If mode === "boundary":
     * - We clamp inside the closest matching boundary element (if found).
     * - Default: ".gadget--expanded"
     */
    boundarySelector?: string;

    /**
     * Movement threshold (px) to count as a drag (and suppress click).
     * Default: 6
     */
    dragThresholdPx?: number;

    /**
     * Inertia only applies to mode === "grab-offset".
     * Default: true
     */
    inertia?: boolean;

    /**
     * Inertia tuning (grab-offset only).
     * friction: 0.90~0.97 typical (higher = longer glide)
     * Default: 0.92
     */
    inertiaFriction?: number;

    /**
     * Stop when speed is below this (px/ms).
     * Default: 0.02
     */
    inertiaStopSpeed?: number;

    /**
     * ✅ NEW: How much of the panel can overflow the viewport?
     * 0.0 = Strict containment (no overflow)
     * 0.5 = 50% of the panel can slide off-screen (Default)
     */
    overflowRatio?: number;
}

export function makePanelDraggable(
    panel: HTMLElement,
    handle: HTMLElement,
    options: DragOptions,
): void {
    const mode = options.mode;
    const boundarySelector = options.boundarySelector ?? ".gadget--expanded";
    const dragThresholdPx = options.dragThresholdPx ?? 6;

    const inertiaEnabled = options.inertia ?? true;
    const inertiaFriction = options.inertiaFriction ?? 0.92;
    const inertiaStopSpeed = options.inertiaStopSpeed ?? 0.02;
    const overflowRatio = options.overflowRatio ?? 0.7;

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

    // ✅ Bounds (Now support min values for overflow)
    let minLeft = 0;
    let maxLeft = 0;
    let minTop = 0;
    let maxTop = 0;

    // boundary mode specific
    let boundaryEl: HTMLElement | null = null;
    let boundaryRect: DOMRect | null = null;

    // click suppression
    let moved = false;
    let suppressNextClick = false;

    // velocity tracking (for inertia)
    let lastMoveT = 0;
    let lastMoveX = 0;
    let lastMoveY = 0;
    let vx = 0; // px/ms
    let vy = 0; // px/ms
    let inertiaRaf: number | null = null;

    let prevUserSelect: string | null = null;

    // ---- helpers ----

    function stopInertia(): void {
        if (inertiaRaf !== null) {
            cancelAnimationFrame(inertiaRaf);
            inertiaRaf = null;
        }
    }

    function clamp(n: number, min: number, max: number): number {
        return Math.max(min, Math.min(max, n));
    }

    function findBoundary(): HTMLElement | null {
        return panel.closest(boundarySelector) as HTMLElement | null;
    }

    function setPanelPositioningForBoundary(bound: HTMLElement | null): void {
        if (bound) {
            const cs = window.getComputedStyle(bound);
            if (cs.position === "static") bound.style.position = "relative";
            // inside boundary box
            panel.style.position = "absolute";
        } else {
            // viewport
            panel.style.position = "fixed";
        }
    }

    function getPanelLeftTopInBoundary(panelRect: DOMRect, boundRect: DOMRect | null) {
        if (!boundRect) return {left: panelRect.left, top: panelRect.top};
        return {left: panelRect.left - boundRect.left, top: panelRect.top - boundRect.top};
    }

    /**
     * ✅ UPDATED: Compute bounds allowing overflow
     */
    function computeBoundsForGrabOffset(): void {
        const vpW = window.innerWidth;
        const vpH = window.innerHeight;

        // Allow sliding Left/Up by overflow ratio
        // Example: If ratio is 0.5, left can go to -width/2
        minLeft = -(panelW * overflowRatio);

        // Keep Header Visible: usually strictly 0 for top to avoid losing the handle
        // If you want top overflow, use: -(panelH * overflowRatio)
        minTop = 0;

        // Allow sliding Right/Down by overflow ratio
        // Max Left = Viewport - (Visible Part)
        maxLeft = vpW - (panelW * (1 - overflowRatio));
        maxTop = vpH - (panelH * (1 - overflowRatio));
    }

    function computeBoundsForBoundaryMode(panelRect: DOMRect): void {
        if (boundaryRect) {
            minLeft = 0;
            minTop = 0;
            maxLeft = Math.max(0, boundaryRect.width - panelRect.width);
            maxTop = Math.max(0, boundaryRect.height - panelRect.height);
        } else {
            minLeft = 0;
            minTop = 0;
            maxLeft = Math.max(0, window.innerWidth - panelRect.width);
            maxTop = Math.max(0, window.innerHeight - panelRect.height);
        }
    }

    function updateVelocity(event: PointerEvent): void {
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

    function startInertiaIfNeeded(): void {
        if (mode !== "grab-offset") return;
        if (!inertiaEnabled) return;
        if (!moved) return;

        // If velocity is tiny, don't animate
        if (Math.abs(vx) < inertiaStopSpeed && Math.abs(vy) < inertiaStopSpeed) return;

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

            // ✅ CLAMP using new Min/Max bounds
            x = clamp(x, minLeft, maxLeft);
            y = clamp(y, minTop, maxTop);

            panel.style.left = `${x}px`;
            panel.style.top = `${y}px`;

            const done =
                Math.abs(vx) < inertiaStopSpeed &&
                Math.abs(vy) < inertiaStopSpeed;

            if (!done) {
                inertiaRaf = requestAnimationFrame(tick);
            } else {
                inertiaRaf = null;
            }
        };

        inertiaRaf = requestAnimationFrame(tick);
    }

    // Suppress click that happens after a drag (this prevents gadget header click-open)
    handle.addEventListener(
        "click",
        (e) => {
            if (!suppressNextClick) return;
            suppressNextClick = false;
            e.preventDefault();
            e.stopPropagation();
        },
        true, // capture!
    );

    // ---- pointer handlers ----

    const onPointerDown = (event: PointerEvent) => {
        // Only left click for mouse; allow touch/pen
        if (event.pointerType === "mouse" && event.button !== 0) return;

        // If you click on interactive controls inside the handle, don't drag
        const target = event.target as HTMLElement | null;
        if (target && target.closest("button, a, input, select, textarea")) return;

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

            // Calculate bounds immediately for boundary mode
            computeBoundsForBoundaryMode(rect);
        } else {
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

            // bounds based on current size with OVERFLOW support
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
        } catch {
            // ignore
        }
    };

    const onPointerMove = (event: PointerEvent) => {
        if (!isDragging) return;

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

            // Use pre-calculated min/max from PointerDown
            nextLeft = clamp(nextLeft, minLeft, maxLeft);
            nextTop = clamp(nextTop, minTop, maxTop);

            panel.style.left = `${nextLeft}px`;
            panel.style.top = `${nextTop}px`;
        } else {
            // grab-offset
            updateVelocity(event);

            let nextLeft = event.clientX - grabOffsetX;
            let nextTop = event.clientY - grabOffsetY;

            // ✅ CLAMP using Overflow bounds
            nextLeft = clamp(nextLeft, minLeft, maxLeft);
            nextTop = clamp(nextTop, minTop, maxTop);

            panel.style.left = `${nextLeft}px`;
            panel.style.top = `${nextTop}px`;
        }
    };

    const onPointerUp = (event: PointerEvent) => {
        if (!isDragging) return;
        isDragging = false;

        // If we moved, suppress the click that would otherwise toggle the gadget
        if (moved) suppressNextClick = true;

        if (prevUserSelect !== null) {
            document.body.style.userSelect = prevUserSelect;
            prevUserSelect = null;
        }

        try {
            handle.releasePointerCapture(event.pointerId);
        } catch {
            // ignore
        }

        if (mode === "boundary") {
            boundaryEl = null;
            boundaryRect = null;
        } else {
            panel.classList.remove("is-dragging");
            startInertiaIfNeeded();
        }
    };


    handle.addEventListener("pointerdown", onPointerDown, {passive: false});
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