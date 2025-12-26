/**
 * Saves the current 'left' and 'top' coordinates to localStorage.
 */
export declare function saveGadgetPosition(el: HTMLElement | null, id: string): void;
/**
 * Restores position from localStorage.
 * STRICTLY overrides CSS defaults (bottom/right/inset) to prevent jumping.
 */
export declare function restoreGadgetPosition(el: HTMLElement | null, id: string): void;
/**
 * Binds the standard "Hover to Peek, Click to Pin" behavior used by
 * Weather, Files, Clock, and Stock gadgets.
 */
export declare function bindStandardGadgetEvents(gadget: HTMLElement, header: HTMLElement, toggleBtn: HTMLElement, backdrop: HTMLElement, storageId: string, onExpand?: () => void): void;
//# sourceMappingURL=gadget_utils.d.ts.map