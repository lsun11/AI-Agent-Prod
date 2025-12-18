// static/desktop.ts
import { ChatUI } from "./chat-ui.js";
import { initHistoryPanel } from "./history.js";
import { makePanelDraggable } from "./drag.js";
import { makePanelResizable } from "./resize.js";
export class Desktop {
    constructor() {
        this.gadget = document.getElementById("ai-gadget");
        this.header = document.getElementById("ai-gadget-header");
        this.toggleBtn = document.getElementById("ai-gadget-toggle");
        this.backdrop = document.getElementById("gadget-backdrop");
        this.initGadgetBehavior();
        this.initComponents();
        this.initDraggables();
    }
    initComponents() {
        // Your AI Agent components still mount using the same IDs inside gadget-body
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
        const EXP_KEYS = ["left", "top", "width", "height", "right", "bottom", "inset"];
        const saveExpandedGeometry = () => {
            const rect = gadget.getBoundingClientRect();
            // save current inline size/pos (preferred), else rect
            const data = {
                left: gadget.style.left || `${rect.left}px`,
                top: gadget.style.top || `${rect.top}px`,
                width: gadget.style.width || `${rect.width}px`,
                height: gadget.style.height || `${rect.height}px`,
            };
            gadget.dataset.expLeft = data.left;
            gadget.dataset.expTop = data.top;
            gadget.dataset.expWidth = data.width;
            gadget.dataset.expHeight = data.height;
        };
        const applyExpandedGeometry = () => {
            const w = gadget.dataset.expWidth;
            const h = gadget.dataset.expHeight;
            if (w)
                gadget.style.width = w;
            if (h)
                gadget.style.height = h;
            // Optional: if you also want expanded position to persist:
            const l = gadget.dataset.expLeft;
            const t = gadget.dataset.expTop;
            if (l)
                gadget.style.left = l;
            if (t)
                gadget.style.top = t;
            // Make expanded state not re-apply inset sizing
            gadget.style.removeProperty("inset");
            gadget.style.right = "auto";
            gadget.style.bottom = "auto";
            gadget.style.position = "fixed";
        };
        const clearInlineGeometry = () => {
            for (const k of EXP_KEYS)
                gadget.style.removeProperty(k);
            gadget.style.position = ""; // let CSS drive collapsed layout
        };
        const slot = document.getElementById("ai-gadget-slot");
        const setExpanded = (expanded) => {
            if (expanded) {
                // going to expanded:
                const raw = localStorage.getItem("ai-gadget-expanded-size");
                if (raw) {
                    try {
                        const { w, h } = JSON.parse(raw);
                        if (w)
                            gadget.style.setProperty("--gadget-exp-w", w);
                        if (h)
                            gadget.style.setProperty("--gadget-exp-h", h);
                    }
                    catch (_a) {
                    }
                }
                // keep whatever expanded size was last saved
                gadget.classList.add("gadget--expanded");
                gadget.classList.remove("gadget--collapsed");
                backdrop.classList.toggle("visible", true);
                if (slot)
                    slot.classList.toggle("is-expanded", expanded);
                // apply saved expanded geometry if it exists
                if (gadget.dataset.expWidth || gadget.dataset.expHeight) {
                    applyExpandedGeometry();
                }
            }
            else {
                // going to collapsed:
                // 🔥 Collapse must ignore any old drag/resize inline styles
                gadget.style.removeProperty("position");
                gadget.style.removeProperty("left");
                gadget.style.removeProperty("top");
                gadget.style.removeProperty("right");
                gadget.style.removeProperty("bottom");
                gadget.style.removeProperty("inset");
                gadget.style.removeProperty("transform");
                gadget.style.removeProperty("width");
                gadget.style.removeProperty("height");
                // save current expanded geometry (so resize persists)
                if (gadget.classList.contains("gadget--expanded")) {
                    saveExpandedGeometry();
                }
                // collapse to universal small size
                gadget.classList.remove("gadget--expanded");
                gadget.classList.add("gadget--collapsed");
                backdrop.classList.toggle("visible", false);
                // critical: remove inline width/height/left/top so it doesn't stay huge
                clearInlineGeometry();
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
        //backdrop.addEventListener("click", () => setExpanded(false));
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
    }
}
//# sourceMappingURL=desktop.js.map