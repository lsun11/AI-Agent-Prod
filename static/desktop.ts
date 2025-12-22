// static/desktop.ts
import { ChatUI } from "./components/advanced-agent/chat-ui.js";
import { initHistoryPanel } from "./components/advanced-agent/history.js";
import { makePanelDraggable } from "./helpers/drag.js";
import { makePanelResizable } from "./helpers/resize.js";
import { WeatherGadget } from "./components/weather_app/weather.js";
import { FilesGadget } from "./components/files_app/files.js";

export class Desktop {
  private gadget: HTMLElement | null;
  private header: HTMLElement | null;
  private toggleBtn: HTMLButtonElement | null;
  private backdrop: HTMLElement | null;
  private weatherGadgetEl: HTMLElement | null;
  private weatherHeaderEl: HTMLElement | null;
  private weatherToggleBtn: HTMLButtonElement | null;
  private weather?: WeatherGadget;
  private filesGadgetEl: HTMLElement | null;
  private filesHeaderEl: HTMLElement | null;
  private filesToggleBtn: HTMLButtonElement | null;
  private files?: FilesGadget;

  private chatUI?: ChatUI;

  constructor() {
    this.gadget = document.getElementById("ai-gadget");
    this.header = document.getElementById("ai-gadget-header");
    this.toggleBtn = document.getElementById("ai-gadget-toggle") as HTMLButtonElement | null;
    this.backdrop = document.getElementById("gadget-backdrop");
    this.weatherGadgetEl = document.getElementById("weather-gadget");
    this.weatherHeaderEl = document.getElementById("weather-gadget-header");
    this.weatherToggleBtn = document.getElementById("weather-gadget-toggle") as HTMLButtonElement | null;
    this.filesGadgetEl = document.getElementById("files-gadget");
    this.filesHeaderEl = document.getElementById("files-gadget-header");
    this.filesToggleBtn = document.getElementById("files-gadget-toggle") as HTMLButtonElement | null;

    // Init Logic
    this.initWeatherBehavior();
    this.initWeatherLogic();
    this.initFilesBehavior();
    this.initFilesLogic();
    this.initGadgetBehavior();
    this.initComponents();
    this.initDraggables();
  }

  private initComponents(): void {
    this.chatUI = new ChatUI();
    void initHistoryPanel();
  }

  private initGadgetBehavior(): void {
    const gadget = this.gadget;
    const header = this.header;
    const toggleBtn = this.toggleBtn;
    const backdrop = this.backdrop;

    if (!gadget || !header || !toggleBtn || !backdrop) return;

    const slot = document.getElementById("ai-gadget-slot");

    const setExpanded = (expanded: boolean) => {
      // 1. POSITION NORMALIZATION (Crucial Fix)
      // Regardless of open/close, freeze the current visual location into explicit Top/Left.
      // We MUST remove 'inset' and 'transform' so they don't override our manual coordinates.
      const rect = gadget.getBoundingClientRect();

      gadget.style.removeProperty("inset");        // Remove the conflicting property
      gadget.style.removeProperty("transform");    // Remove drag transforms
      gadget.style.removeProperty("right");        // Ensure no edge constraints
      gadget.style.removeProperty("bottom");

      gadget.style.left = `${rect.left}px`;        // Hard-set current pixels
      gadget.style.top = `${rect.top}px`;
      gadget.style.position = "fixed";             // Lock it to viewport

      if (expanded) {
        // --- OPENING ---
        // Restore saved size if it exists
        const raw = localStorage.getItem("ai-gadget-expanded-size");
        if (raw) {
          try {
            const { w, h } = JSON.parse(raw);
            if (w) gadget.style.width = w;
            if (h) gadget.style.height = h;
          } catch {}
        }

        gadget.classList.add("gadget--expanded");
        gadget.classList.remove("gadget--collapsed");
        backdrop.classList.toggle("visible", true);

        if (slot) slot.classList.toggle("is-expanded", expanded);

        // Clear constraints that might limit expansion
        gadget.style.removeProperty("min-width");
        gadget.style.removeProperty("min-height");

      } else {
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
      if (e.target === toggleBtn) return;
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
      const title = gadget.querySelector(".gadget-title")?.textContent?.trim() ?? "";
      const meta = gadget.querySelector(".gadget-meta")?.textContent?.trim() ?? "";
      gadget.setAttribute("data-title", title);
      gadget.setAttribute("data-meta", meta);
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setExpanded(false);
    });
  }

  private initDraggables(): void {
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
  }

  private initWeatherLogic(): void {
    if (this.weatherGadgetEl) {
      this.weather = new WeatherGadget(this.weatherGadgetEl);
    }
  }

private initWeatherBehavior(): void {
    const gadget = this.weatherGadgetEl;
    const header = this.weatherHeaderEl;
    const toggleBtn = this.weatherToggleBtn;
    const backdrop = this.backdrop;

    if (!gadget || !header || !toggleBtn || !backdrop) return;

    // ✅ CHANGED: Added state for Hover vs Click
    let hoverTimeout: number | undefined;
    let isPinned = false;

    const setExpanded = (expanded: boolean, pinned: boolean = false) => {
      // ✅ CHANGED: FREEZE POSITION LOGIC
      // This runs EVERY time you open or close. It captures the current
      // visual location and hard-codes it to top/left, deleting 'inset'.
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
        isPinned = pinned; // Track if this was a click (pin) or hover (peek)

        const raw = localStorage.getItem("weather-gadget-expanded-size");
        if (raw) {
          try {
            const { w, h } = JSON.parse(raw);
            if (w) gadget.style.width = w;
            if (h) gadget.style.height = h;
          } catch {}
        }

        gadget.classList.add("gadget--expanded");
        gadget.classList.remove("gadget--collapsed");

        // Show backdrop ONLY if pinned
        if (isPinned) backdrop.classList.add("visible");

        gadget.style.removeProperty("min-width");
        gadget.style.removeProperty("min-height");

        void this.weather?.refresh(false);

      } else {
        // --- CLOSING ---
        isPinned = false;

        if (gadget.classList.contains("gadget--expanded")) {
            const rect = gadget.getBoundingClientRect();
            const size = { w: `${rect.width}px`, h: `${rect.height}px` };
            localStorage.setItem("weather-gadget-expanded-size", JSON.stringify(size));
        }

        // Wipe SIZE only. Keep the POSITION (left/top) we set above.
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
      const isCurrentlyExpanded = gadget.classList.contains("gadget--expanded");
      if (isCurrentlyExpanded) {
        setExpanded(false);
      } else {
        setExpanded(true, true); // true = Pinned
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

    gadget.addEventListener("mouseenter", () => {
        if (gadget.classList.contains("is-dragging") || gadget.classList.contains("gadget--expanded")) return;

        // Open after 2 seconds (Pinned = false)
        hoverTimeout = window.setTimeout(() => {
            if (!gadget.classList.contains("is-dragging")) {
                setExpanded(true, false);
            }
        }, 600);
    });

    gadget.addEventListener("mouseleave", () => {
        clearTimeout(hoverTimeout);

        if (gadget.classList.contains("is-dragging")) return;

        // Close ONLY if it wasn't pinned (clicked)
        if (gadget.classList.contains("gadget--expanded") && !isPinned) {
            setExpanded(false);
        }
    });
  }

  private initFilesLogic(): void {
    if (this.filesGadgetEl) {
        this.files = new FilesGadget(this.filesGadgetEl);
    }
  }

  private initFilesBehavior(): void {
    const gadget = this.filesGadgetEl;
    const header = this.filesHeaderEl;
    const toggleBtn = this.filesToggleBtn;
    const backdrop = this.backdrop;

    if (!gadget || !header || !toggleBtn || !backdrop) return;

    let hoverTimeout: number | undefined;
    let isPinned = false;

    const setExpanded = (expanded: boolean, pinned: boolean = false) => {
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
            if (w) gadget.style.width = w;
            if (h) gadget.style.height = h;
          } catch {}
        }

        gadget.classList.add("gadget--expanded");
        gadget.classList.remove("gadget--collapsed");

        // Show backdrop ONLY if pinned
        if (isPinned) backdrop.classList.add("visible");
        else backdrop.classList.remove("visible"); // Ensure hidden if just peeking

        gadget.style.removeProperty("min-width");
        gadget.style.removeProperty("min-height");

        this.files?.refresh();

      } else {
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

    // ✅ FIXED: Toggle Logic to handle "Peek -> Pin" transition
    const toggle = () => {
      const isExpanded = gadget.classList.contains("gadget--expanded");

      if (isExpanded && isPinned) {
         // It was fully open/pinned, so close it.
         setExpanded(false);
      } else {
         // It was closed OR it was just peeking (hovered).
         // In both cases, we want to force it OPEN and PINNED.
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

    // Hover (Peek)
    gadget.addEventListener("mouseenter", () => {
        if (gadget.classList.contains("is-dragging")) return;

        // Only peek if not already open
        if (!gadget.classList.contains("gadget--expanded")) {
            hoverTimeout = window.setTimeout(() => {
                if (!gadget.classList.contains("is-dragging")) {
                    setExpanded(true, false); // Peek (not pinned)
                }
            }, 2000);
        }
    });

    gadget.addEventListener("mouseleave", () => {
        clearTimeout(hoverTimeout);
        if (gadget.classList.contains("is-dragging")) return;

        // Close ONLY if it wasn't pinned
        if (gadget.classList.contains("gadget--expanded") && !isPinned) {
            setExpanded(false);
        }
    });
  }
}