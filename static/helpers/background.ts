// static/helpers/background.ts

let currentTopicKey: string | null = null;

/**
 * Switches the document body class to trigger the CSS background transition.
 */
export function switchBackground(key: string): void {
    if (currentTopicKey === key) return;

    // Remove old class
    if (currentTopicKey) {
        document.body.classList.remove(`topic-bg-${currentTopicKey}`);
    }

    // Add new class
    const newClass = `topic-bg-${key}`;
    document.body.classList.add(newClass);

    currentTopicKey = key;
}

/**
 * Removes the current background class, reverting to the default CSS.
 */
export function resetBackground(): void {
    if (currentTopicKey) {
        document.body.classList.remove(`topic-bg-${currentTopicKey}`);
        currentTopicKey = null;
    }
}

/**
 * Attaches listeners with a 2-second delay on hover and immediate reset on leave.
 */
export function attachBackgroundListeners(gadget: HTMLElement | null, id: string) {
    if (!gadget) return;

    let hoverTimer: number | null = null;

    // 1. Mouse Enter: Wait 2 seconds before switching
    gadget.addEventListener("mouseenter", () => {
        // Clear any existing timer just in case
        if (hoverTimer) clearTimeout(hoverTimer);

        hoverTimer = window.setTimeout(() => {
            switchBackground(id);
        }, 1000);
    });

    // 2. Mouse Leave: Cancel timer AND reset background immediately
    gadget.addEventListener("mouseleave", () => {
        if (hoverTimer) {
            clearTimeout(hoverTimer);
            hoverTimer = null;
        }
        // Immediately revert to default background
        resetBackground();
    });

    // 3. Interaction (Click/Touch): Switch IMMEDIATELY
    const immediateTrigger = () => {
        if (hoverTimer) clearTimeout(hoverTimer);
        switchBackground(id);
    };

    gadget.addEventListener("mousedown", immediateTrigger);
    gadget.addEventListener("touchstart", immediateTrigger, { passive: true });
}