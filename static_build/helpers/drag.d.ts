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
export declare function makePanelDraggable(panel: HTMLElement, handle: HTMLElement, options: DragOptions): void;
export {};
//# sourceMappingURL=drag.d.ts.map