/**
 * Make a panel draggable using the given handle element.
 *
 * - panel: the element that actually moves
 * - handle: the element the user drags (e.g. header/title bar)
 */
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
export declare function makePanelDraggable(panel: HTMLElement, handle: HTMLElement): void;
//# sourceMappingURL=drag.d.ts.map