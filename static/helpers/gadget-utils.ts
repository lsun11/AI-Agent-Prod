// static/helpers/gadget-utils.ts

/**
 * Saves the current 'left' and 'top' coordinates to localStorage.
 */
export function saveGadgetPosition(el: HTMLElement | null, id: string) {
    if (!el) return;
    const rect = el.getBoundingClientRect();

    // Ensure we are saving finite numbers
    if (Number.isFinite(rect.left) && Number.isFinite(rect.top)) {
        const pos = { left: rect.left, top: rect.top };
        localStorage.setItem(`pos-${id}`, JSON.stringify(pos));
    }
}

/**
 * Restores position from localStorage.
 * STRICTLY overrides CSS defaults (bottom/right/inset) to prevent jumping.
 */
export function restoreGadgetPosition(el: HTMLElement | null, id: string) {
    if (!el) return;

    const raw = localStorage.getItem(`pos-${id}`);
    if (!raw) return;

    try {
        const pos = JSON.parse(raw);
        let left = parseFloat(pos.left) || 0;
        let top = parseFloat(pos.top) || 0;

        // Safety: Reset to center if coordinates are corrupt/zero
        if (!Number.isFinite(left) || !Number.isFinite(top) || (left === 0 && top === 0)) {
            left = window.innerWidth / 2 - 150;
            top = window.innerHeight / 2 - 150;
        }

        setTimeout(() => {
            el.style.setProperty("inset", "auto", "important");
            el.style.setProperty("bottom", "auto", "important");
            el.style.setProperty("right", "auto", "important");

            // Apply specific coordinates
            el.style.setProperty("position", "fixed", "important");
            el.style.setProperty("left", `${left}px`, "important");
            el.style.setProperty("top", `${top}px`, "important");
            el.style.setProperty("margin", "0", "important");

            // Clear transform so it doesn't double-apply offsets
            el.style.transform = "none";
        }, 100);

    } catch (e) {
        console.error(`Failed to restore position for ${id}`, e);
    }
}

/**
 * Binds the standard "Hover to Peek, Click to Pin" behavior used by
 * Weather, Files, Clock, and Stock gadgets.
 */
export function bindStandardGadgetEvents(
    gadget: HTMLElement,
    header: HTMLElement,
    toggleBtn: HTMLElement,
    backdrop: HTMLElement,
    storageId: string,
    onExpand?: () => void
) {
    let hoverTimeout: number | undefined;
    let isPinned = false;

    const setExpanded = (expanded: boolean, pinned: boolean = false) => {
        // Stop the timer!
        clearTimeout(hoverTimeout);

        // 1. FREEZE POSITION LOGIC
        const rect = gadget.getBoundingClientRect();
        gadget.style.removeProperty("inset");
        gadget.style.removeProperty("transform");
        gadget.style.removeProperty("right");
        gadget.style.removeProperty("bottom");
        gadget.style.left = `${rect.left}px`;
        gadget.style.top = `${rect.top}px`;
        gadget.style.position = "fixed";

        saveGadgetPosition(gadget, storageId);

        if (expanded) {
            // --- OPENING ---
            isPinned = pinned;

            const raw = localStorage.getItem(`${storageId}-expanded-size`);
            if (raw) {
                try {
                    const { w, h } = JSON.parse(raw);
                    if (w) gadget.style.width = w;
                    if (h) gadget.style.height = h;
                } catch {}
            }

            gadget.classList.add("gadget--expanded");
            gadget.classList.remove("gadget--collapsed");

            if (isPinned) backdrop.classList.add("visible");
            else backdrop.classList.remove("visible");

            gadget.style.removeProperty("min-width");
            gadget.style.removeProperty("min-height");

            if (onExpand) onExpand();

        } else {
            // --- CLOSING ---
            isPinned = false;

            if (gadget.classList.contains("gadget--expanded")) {
                const rect = gadget.getBoundingClientRect();
                const size = { w: `${rect.width}px`, h: `${rect.height}px` };
                localStorage.setItem(`${storageId}-expanded-size`, JSON.stringify(size));
            }

            gadget.style.removeProperty("width");
            gadget.style.removeProperty("height");
            gadget.style.removeProperty("min-width");
            gadget.style.removeProperty("min-height");

            gadget.classList.remove("gadget--expanded");
            gadget.classList.add("gadget--collapsed");
            backdrop.classList.remove("visible");
        }

        gadget.setAttribute("aria-expanded", expanded ? "true" : "false");
        toggleBtn.textContent = expanded ? "Close" : "Open";
    };

    const toggle = () => {
        const isExpanded = gadget.classList.contains("gadget--expanded");

        // If currently open AND pinned -> Close
        if (isExpanded && isPinned) {
            setExpanded(false);
        }
        // If closed OR only peeking -> Open and Pin
        else {
            setExpanded(true, true);
        }
    };

    header.addEventListener("click", (e) => {
        if (e.target === toggleBtn) return;
        toggle();
    });

    toggleBtn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggle();
    });

    backdrop.addEventListener("click", () => setExpanded(false));

    // HOVER LOGIC
    gadget.addEventListener("mouseenter", () => {
        if (gadget.classList.contains("is-dragging")) return;

        // Start timer to Peek
        if (!gadget.classList.contains("gadget--expanded")) {
            hoverTimeout = window.setTimeout(() => {
                if (!gadget.classList.contains("is-dragging")) {
                    setExpanded(true, false); // false = Not Pinned (Peek)
                }
            }, 600);
        }
    });

    gadget.addEventListener("mouseleave", () => {
        // Cancel timer if we leave before it fires
        clearTimeout(hoverTimeout);

        if (gadget.classList.contains("is-dragging")) return;

        // Close ONLY if we are just Peeking (!isPinned)
        if (gadget.classList.contains("gadget--expanded") && !isPinned) {
            setExpanded(false);
        }
    });
}