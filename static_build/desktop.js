// static/desktop.ts
import { ChatUI } from "./components/advanced-agent/chat-ui.js";
import { initHistoryPanel } from "./components/advanced-agent/history.js";
import { makePanelDraggable } from "./helpers/drag.js";
import { makePanelResizable } from "./helpers/resize.js";
import { WeatherGadget } from "./components/weather_app/weather.js";
import { FilesGadget } from "./components/files_app/files.js";
import { ClockGadget } from "./components/clock_app/clock.js";
export class Desktop {
    constructor() {
        this.gadget = document.getElementById("ai-gadget");
        this.header = document.getElementById("ai-gadget-header");
        this.toggleBtn = document.getElementById("ai-gadget-toggle");
        this.backdrop = document.getElementById("gadget-backdrop");
        this.weatherGadgetEl = document.getElementById("weather-gadget");
        this.weatherHeaderEl = document.getElementById("weather-gadget-header");
        this.weatherToggleBtn = document.getElementById("weather-gadget-toggle");
        this.filesGadgetEl = document.getElementById("files-gadget");
        this.filesHeaderEl = document.getElementById("files-gadget-header");
        this.filesToggleBtn = document.getElementById("files-gadget-toggle");
        this.clockGadgetEl = document.getElementById("clock-gadget");
        this.clockHeaderEl = document.getElementById("clock-gadget-header");
        this.clockToggleBtn = document.getElementById("clock-gadget-toggle");
        // Init Logic
        this.initWeatherBehavior();
        this.initWeatherLogic();
        this.initFilesBehavior();
        this.initFilesLogic();
        this.initGadgetBehavior();
        this.initComponents();
        this.initDraggables();
        this.initClockBehavior(); // New Behavior
        this.initClockLogic();
    }
    initComponents() {
        this.chatUI = new ChatUI();
        void initHistoryPanel();
    }
    initGadgetBehavior() {
        var _a, _b, _c, _d, _e, _f;
        const gadget = this.gadget;
        const header = this.header;
        const toggleBtn = this.toggleBtn;
        const backdrop = this.backdrop;
        if (!gadget || !header || !toggleBtn || !backdrop)
            return;
        const slot = document.getElementById("ai-gadget-slot");
        const setExpanded = (expanded) => {
            // 1. POSITION NORMALIZATION (Crucial Fix)
            // Regardless of open/close, freeze the current visual location into explicit Top/Left.
            // We MUST remove 'inset' and 'transform' so they don't override our manual coordinates.
            const rect = gadget.getBoundingClientRect();
            gadget.style.removeProperty("inset"); // Remove the conflicting property
            gadget.style.removeProperty("transform"); // Remove drag transforms
            gadget.style.removeProperty("right"); // Ensure no edge constraints
            gadget.style.removeProperty("bottom");
            gadget.style.left = `${rect.left}px`; // Hard-set current pixels
            gadget.style.top = `${rect.top}px`;
            gadget.style.position = "fixed"; // Lock it to viewport
            if (expanded) {
                // --- OPENING ---
                // Restore saved size if it exists
                const raw = localStorage.getItem("ai-gadget-expanded-size");
                if (raw) {
                    try {
                        const { w, h } = JSON.parse(raw);
                        if (w)
                            gadget.style.width = w;
                        if (h)
                            gadget.style.height = h;
                    }
                    catch (_a) { }
                }
                gadget.classList.add("gadget--expanded");
                gadget.classList.remove("gadget--collapsed");
                backdrop.classList.toggle("visible", true);
                if (slot)
                    slot.classList.toggle("is-expanded", expanded);
                // Clear constraints that might limit expansion
                gadget.style.removeProperty("min-width");
                gadget.style.removeProperty("min-height");
            }
            else {
                // --- CLOSING ---
                if (gadget.classList.contains("gadget--expanded")) {
                    // Save ONLY the dimensions (width/height)
                    const rect = gadget.getBoundingClientRect();
                    const size = { w: `${rect.width}px`, h: `${rect.height}px` };
                    localStorage.setItem("ai-gadget-expanded-size", JSON.stringify(size));
                }
                // Wipe dimensions so CSS class can collapse it.
                // DO NOT wipe left/top/position - we just set them above to keep it in place.
                gadget.style.removeProperty("width");
                gadget.style.removeProperty("height");
                gadget.style.removeProperty("min-width");
                gadget.style.removeProperty("min-height");
                gadget.classList.remove("gadget--expanded");
                gadget.classList.add("gadget--collapsed");
                backdrop.classList.toggle("visible", false);
            }
            gadget.setAttribute("aria-expanded", expanded ? "true" : "false");
            toggleBtn.textContent = expanded ? "Close" : "Open";
            document.documentElement.classList.toggle("no-scroll", expanded);
            document.body.classList.toggle("no-scroll", expanded);
        };
        const toggle = () => {
            const expanded = gadget.classList.contains("gadget--expanded");
            setExpanded(expanded);
        };
        header.addEventListener("click", (e) => {
            if (e.target === toggleBtn)
                return;
            toggle();
        });
        toggleBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggle();
        });
        header.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                toggle();
            }
        });
        if (gadget) {
            const title = (_c = (_b = (_a = gadget.querySelector(".gadget-title")) === null || _a === void 0 ? void 0 : _a.textContent) === null || _b === void 0 ? void 0 : _b.trim()) !== null && _c !== void 0 ? _c : "";
            const meta = (_f = (_e = (_d = gadget.querySelector(".gadget-meta")) === null || _d === void 0 ? void 0 : _d.textContent) === null || _e === void 0 ? void 0 : _e.trim()) !== null && _f !== void 0 ? _f : "";
            gadget.setAttribute("data-title", title);
            gadget.setAttribute("data-meta", meta);
        }
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape")
                setExpanded(false);
        });
    }
    initDraggables() {
        const gadget = this.gadget;
        const header = this.header;
        if (gadget && header) {
            makePanelDraggable(gadget, header, {
                mode: "grab-offset",
                inertia: true,
                inertiaFriction: 0.92,
                inertiaStopSpeed: 0.05,
            });
            makePanelResizable(gadget, { minWidth: 360, minHeight: 260 });
        }
        if (this.weatherGadgetEl && this.weatherHeaderEl) {
            makePanelDraggable(this.weatherGadgetEl, this.weatherHeaderEl, {
                mode: "grab-offset",
                inertia: true,
                inertiaFriction: 0.92,
                inertiaStopSpeed: 0.05,
            });
            makePanelResizable(this.weatherGadgetEl, { minWidth: 160, minHeight: 220 });
        }
        if (this.filesGadgetEl && this.filesHeaderEl) {
            makePanelDraggable(this.filesGadgetEl, this.filesHeaderEl, {
                mode: "grab-offset",
                inertia: true,
                inertiaFriction: 0.92,
                inertiaStopSpeed: 0.05,
            });
            makePanelResizable(this.filesGadgetEl, { minWidth: 300, minHeight: 200 });
        }
        if (this.clockGadgetEl && this.clockHeaderEl) {
            makePanelDraggable(this.clockGadgetEl, this.clockHeaderEl, {
                mode: "grab-offset",
                inertia: true,
                inertiaFriction: 0.92,
                inertiaStopSpeed: 0.05,
            });
            makePanelResizable(this.clockGadgetEl, { minWidth: 200, minHeight: 200 });
        }
    }
    initWeatherLogic() {
        if (this.weatherGadgetEl) {
            this.weather = new WeatherGadget(this.weatherGadgetEl);
        }
    }
    initWeatherBehavior() {
        const gadget = this.weatherGadgetEl;
        const header = this.weatherHeaderEl;
        const toggleBtn = this.weatherToggleBtn;
        const backdrop = this.backdrop;
        if (!gadget || !header || !toggleBtn || !backdrop)
            return;
        let hoverTimeout;
        let isPinned = false;
        const setExpanded = (expanded, pinned = false) => {
            var _a;
            // ✅ CRITICAL FIX: Stop the timer!
            // If the user clicks (Pin), we must cancel any pending "Peek" timer
            // so it doesn't overwrite our state 600ms later.
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
            if (expanded) {
                // --- OPENING ---
                isPinned = pinned;
                const raw = localStorage.getItem("weather-gadget-expanded-size");
                if (raw) {
                    try {
                        const { w, h } = JSON.parse(raw);
                        if (w)
                            gadget.style.width = w;
                        if (h)
                            gadget.style.height = h;
                    }
                    catch (_b) { }
                }
                gadget.classList.add("gadget--expanded");
                gadget.classList.remove("gadget--collapsed");
                if (isPinned)
                    backdrop.classList.add("visible");
                gadget.style.removeProperty("min-width");
                gadget.style.removeProperty("min-height");
                void ((_a = this.weather) === null || _a === void 0 ? void 0 : _a.refresh(false));
            }
            else {
                // --- CLOSING ---
                isPinned = false;
                if (gadget.classList.contains("gadget--expanded")) {
                    const rect = gadget.getBoundingClientRect();
                    const size = { w: `${rect.width}px`, h: `${rect.height}px` };
                    localStorage.setItem("weather-gadget-expanded-size", JSON.stringify(size));
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
            if (e.target === toggleBtn)
                return;
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
            if (gadget.classList.contains("is-dragging"))
                return;
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
            if (gadget.classList.contains("is-dragging"))
                return;
            // Close ONLY if we are just Peeking (!isPinned)
            if (gadget.classList.contains("gadget--expanded") && !isPinned) {
                setExpanded(false);
            }
        });
    }
    initFilesLogic() {
        if (this.filesGadgetEl) {
            this.files = new FilesGadget(this.filesGadgetEl);
        }
    }
    initFilesBehavior() {
        const gadget = this.filesGadgetEl;
        const header = this.filesHeaderEl;
        const toggleBtn = this.filesToggleBtn;
        const backdrop = this.backdrop;
        if (!gadget || !header || !toggleBtn || !backdrop)
            return;
        let hoverTimeout;
        let isPinned = false;
        const setExpanded = (expanded, pinned = false) => {
            var _a;
            // 1. FREEZE POSITION
            const rect = gadget.getBoundingClientRect();
            gadget.style.removeProperty("inset");
            gadget.style.removeProperty("transform");
            gadget.style.removeProperty("right");
            gadget.style.removeProperty("bottom");
            gadget.style.left = `${rect.left}px`;
            gadget.style.top = `${rect.top}px`;
            gadget.style.position = "fixed";
            if (expanded) {
                // --- OPENING ---
                isPinned = pinned;
                // Restore Size
                const raw = localStorage.getItem("files-gadget-expanded-size");
                if (raw) {
                    try {
                        const { w, h } = JSON.parse(raw);
                        if (w)
                            gadget.style.width = w;
                        if (h)
                            gadget.style.height = h;
                    }
                    catch (_b) { }
                }
                gadget.classList.add("gadget--expanded");
                gadget.classList.remove("gadget--collapsed");
                // Show backdrop ONLY if pinned
                if (isPinned)
                    backdrop.classList.add("visible");
                else
                    backdrop.classList.remove("visible"); // Ensure hidden if just peeking
                gadget.style.removeProperty("min-width");
                gadget.style.removeProperty("min-height");
                (_a = this.files) === null || _a === void 0 ? void 0 : _a.refresh();
            }
            else {
                // --- CLOSING ---
                isPinned = false;
                if (gadget.classList.contains("gadget--expanded")) {
                    const rect = gadget.getBoundingClientRect();
                    const size = { w: `${rect.width}px`, h: `${rect.height}px` };
                    localStorage.setItem("files-gadget-expanded-size", JSON.stringify(size));
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
            if (isExpanded && isPinned) {
                // It was fully open/pinned, so close it.
                setExpanded(false);
            }
            else {
                // It was closed OR it was just peeking (hovered).
                // In both cases, we want to force it OPEN and PINNED.
                setExpanded(true, true);
            }
        };
        header.addEventListener("click", (e) => {
            if (e.target === toggleBtn)
                return;
            toggle();
        });
        toggleBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggle();
        });
        backdrop.addEventListener("click", () => setExpanded(false));
        // Hover (Peek)
        gadget.addEventListener("mouseenter", () => {
            if (gadget.classList.contains("is-dragging"))
                return;
            // Only peek if not already open
            if (!gadget.classList.contains("gadget--expanded")) {
                hoverTimeout = window.setTimeout(() => {
                    if (!gadget.classList.contains("is-dragging")) {
                        setExpanded(true, false); // Peek (not pinned)
                    }
                }, 1000);
            }
        });
        gadget.addEventListener("mouseleave", () => {
            clearTimeout(hoverTimeout);
            if (gadget.classList.contains("is-dragging"))
                return;
            // Close ONLY if it wasn't pinned
            if (gadget.classList.contains("gadget--expanded") && !isPinned) {
                setExpanded(false);
            }
        });
    }
    initClockLogic() {
        if (this.clockGadgetEl) {
            this.clock = new ClockGadget(this.clockGadgetEl);
        }
    }
    initClockBehavior() {
        const gadget = this.clockGadgetEl;
        const header = this.clockHeaderEl;
        const toggleBtn = this.clockToggleBtn;
        const backdrop = this.backdrop;
        if (!gadget || !header || !toggleBtn || !backdrop)
            return;
        let hoverTimeout;
        let isPinned = false;
        const setExpanded = (expanded, pinned = false) => {
            // 1. FREEZE POSITION
            const rect = gadget.getBoundingClientRect();
            gadget.style.removeProperty("inset");
            gadget.style.removeProperty("transform");
            gadget.style.removeProperty("right");
            gadget.style.removeProperty("bottom");
            gadget.style.left = `${rect.left}px`;
            gadget.style.top = `${rect.top}px`;
            gadget.style.position = "fixed";
            if (expanded) {
                // --- OPENING ---
                isPinned = pinned;
                const raw = localStorage.getItem("clock-gadget-expanded-size");
                if (raw) {
                    try {
                        const { w, h } = JSON.parse(raw);
                        if (w)
                            gadget.style.width = w;
                        if (h)
                            gadget.style.height = h;
                    }
                    catch (_a) { }
                }
                gadget.classList.add("gadget--expanded");
                gadget.classList.remove("gadget--collapsed");
                if (isPinned)
                    backdrop.classList.add("visible");
                else
                    backdrop.classList.remove("visible");
                gadget.style.removeProperty("min-width");
                gadget.style.removeProperty("min-height");
            }
            else {
                // --- CLOSING ---
                isPinned = false;
                if (gadget.classList.contains("gadget--expanded")) {
                    const rect = gadget.getBoundingClientRect();
                    const size = { w: `${rect.width}px`, h: `${rect.height}px` };
                    localStorage.setItem("clock-gadget-expanded-size", JSON.stringify(size));
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
        // Toggle
        const toggle = () => {
            const isExpanded = gadget.classList.contains("gadget--expanded");
            if (isExpanded && isPinned) {
                setExpanded(false);
            }
            else {
                setExpanded(true, true);
            }
        };
        header.addEventListener("click", (e) => {
            if (e.target === toggleBtn)
                return;
            toggle();
        });
        toggleBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggle();
        });
        backdrop.addEventListener("click", () => setExpanded(false));
        // // Hover
        // gadget.addEventListener("mouseenter", () => {
        //     if (gadget.classList.contains("is-dragging")) return;
        //     if (!gadget.classList.contains("gadget--expanded")) {
        //         hoverTimeout = window.setTimeout(() => {
        //             if (!gadget.classList.contains("is-dragging")) {
        //                 setExpanded(true, false);
        //             }
        //         }, 2000);
        //     }
        // });
        gadget.addEventListener("mouseleave", () => {
            clearTimeout(hoverTimeout);
            if (gadget.classList.contains("is-dragging"))
                return;
            if (gadget.classList.contains("gadget--expanded") && !isPinned) {
                setExpanded(false);
            }
        });
    }
}
//# sourceMappingURL=desktop.js.map