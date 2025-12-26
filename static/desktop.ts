// static/desktop.ts
import {ChatUI} from "./components/advanced-agent/chat-ui.js";
import {initHistoryPanel} from "./components/advanced-agent/history.js";
import {makePanelDraggable} from "./helpers/drag.js";
import {makePanelResizable} from "./helpers/resize.js";
import {WeatherGadget} from "./components/weather_app/weather.js";
import {FilesGadget} from "./components/files_app/files.js";
import {ClockGadget} from "./components/clock_app/clock.js";
import {StockGadget} from "./components/stock_app/stock.js";
import {NewsGadget} from "./components/news_app/news.js";
import { attachBackgroundListeners } from "./helpers/background.js";
import {bindStandardGadgetEvents, restoreGadgetPosition, saveGadgetPosition} from "./helpers/gadget-utils.js";

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

  private clockGadgetEl: HTMLElement | null;
  private clockHeaderEl: HTMLElement | null;
  private clockToggleBtn: HTMLButtonElement | null;
  private clock?: ClockGadget;

  private chatUI?: ChatUI;

  private stockGadgetEl: HTMLElement | null;
  private stockHeaderEl: HTMLElement | null;
  private stockToggleBtn: HTMLButtonElement | null;
  private stock?: StockGadget;

  private newsGadgetEl: HTMLElement | null;
  private newsHeaderEl: HTMLElement | null;
  private newsToggleBtn: HTMLButtonElement | null;
  private news?: NewsGadget;

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

    this.clockGadgetEl = document.getElementById("clock-gadget");
    this.clockHeaderEl = document.getElementById("clock-gadget-header");
    this.clockToggleBtn = document.getElementById("clock-gadget-toggle") as HTMLButtonElement | null;

    this.stockGadgetEl = document.getElementById("stock-gadget");
    this.stockHeaderEl = document.getElementById("stock-gadget-header");
    this.stockToggleBtn = document.getElementById("stock-gadget-toggle") as HTMLButtonElement | null;

    this.newsGadgetEl = document.getElementById("news-gadget");
    this.newsHeaderEl = document.getElementById("news-gadget-header");
    this.newsToggleBtn = document.getElementById("news-gadget-toggle") as HTMLButtonElement | null;

    // Init Logic
    this.initWeatherBehavior();
    this.initWeatherLogic();
    this.initFilesBehavior();
    this.initFilesLogic();
    this.initGadgetBehavior();
    this.initComponents();
    this.initDraggables();
    this.initClockBehavior();
    this.initClockLogic();
    this.initStockBehavior();
    this.initStockLogic();
    this.initNewsBehavior();
    this.initNewsLogic();
    attachBackgroundListeners(this.weatherGadgetEl, "weather-gadget");
    attachBackgroundListeners(this.newsGadgetEl, "news-gadget");
    attachBackgroundListeners(this.filesGadgetEl, "files-gadget");
    attachBackgroundListeners(this.stockGadgetEl, "stock-gadget");
    attachBackgroundListeners(this.clockGadgetEl, "clock-gadget");
    restoreGadgetPosition(this.gadget, "ai-gadget");
    restoreGadgetPosition(this.weatherGadgetEl, "weather-gadget");
    restoreGadgetPosition(this.filesGadgetEl, "files-gadget");
    restoreGadgetPosition(this.clockGadgetEl, "clock-gadget");
    restoreGadgetPosition(this.stockGadgetEl, "stock-gadget");
  }

  private initComponents(): void {
    this.chatUI = new ChatUI();
    void initHistoryPanel();
  }

    // NOTE: AI Gadget has unique logic (slot, escape key) so we kept most of it here,
    // but updated it to use the shared position saver.
  private initGadgetBehavior(): void {
    const gadget = this.gadget;
    const header = this.header;
    const toggleBtn = this.toggleBtn;
    const backdrop = this.backdrop;

    if (!gadget || !header || !toggleBtn || !backdrop) return;

    const slot = document.getElementById("ai-gadget-slot");

    const setExpanded = (expanded: boolean) => {
      // 1. POSITION NORMALIZATION
      const rect = gadget.getBoundingClientRect();

        gadget.style.removeProperty("inset");
        gadget.style.removeProperty("transform");
        gadget.style.removeProperty("right");
        gadget.style.removeProperty("bottom");

        gadget.style.left = `${rect.left}px`;
        gadget.style.top = `${rect.top}px`;
        gadget.style.position = "fixed";

        saveGadgetPosition(gadget, "ai-gadget"); // ✅ Shared function

      if (expanded) {
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

        gadget.style.removeProperty("min-width");
        gadget.style.removeProperty("min-height");

      } else {
        if (gadget.classList.contains("gadget--expanded")) {
            const rect = gadget.getBoundingClientRect();
            const size = { w: `${rect.width}px`, h: `${rect.height}px` };
            localStorage.setItem("ai-gadget-expanded-size", JSON.stringify(size));
        }

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
    const attachSaveListener = (gadget: HTMLElement, id: string) => {
        const onInteractStart = () => {

            const onInteractEnd = () => {
                setTimeout(() => saveGadgetPosition(gadget, id), 200); // ✅ Shared function
                window.removeEventListener("mouseup", onInteractEnd);
                window.removeEventListener("touchend", onInteractEnd);
            };
            window.addEventListener("mouseup", onInteractEnd);
            window.addEventListener("touchend", onInteractEnd);
        };
        gadget.addEventListener("mousedown", onInteractStart);
        gadget.addEventListener("touchstart", onInteractStart);
    };

    // 1. AI Gadget
    if (this.gadget && this.header) {
      makePanelDraggable(this.gadget, this.header, { mode: "grab-offset", inertia: true });
      makePanelResizable(this.gadget, { minWidth: 360, minHeight: 260 });
      attachSaveListener(this.gadget, "ai-gadget");
    }

    // 2. Weather Gadget
    if (this.weatherGadgetEl && this.weatherHeaderEl) {
      makePanelDraggable(this.weatherGadgetEl, this.weatherHeaderEl, { mode: "grab-offset", inertia: true });
      makePanelResizable(this.weatherGadgetEl, { minWidth: 160, minHeight: 220 });
      attachSaveListener(this.weatherGadgetEl, "weather-gadget");
    }

    // 3. Files Gadget
    if (this.filesGadgetEl && this.filesHeaderEl) {
      makePanelDraggable(this.filesGadgetEl, this.filesHeaderEl, { mode: "grab-offset", inertia: true });
      makePanelResizable(this.filesGadgetEl, { minWidth: 300, minHeight: 200 });
      attachSaveListener(this.filesGadgetEl, "files-gadget");
    }

    // 4. Clock Gadget
    if (this.clockGadgetEl && this.clockHeaderEl) {
      makePanelDraggable(this.clockGadgetEl, this.clockHeaderEl, { mode: "grab-offset", inertia: true });
      makePanelResizable(this.clockGadgetEl, { minWidth: 200, minHeight: 200 });
      attachSaveListener(this.clockGadgetEl, "clock-gadget");
    }

    // 5. Stock Gadget
    if (this.stockGadgetEl && this.stockHeaderEl) {
        makePanelDraggable(this.stockGadgetEl, this.stockHeaderEl, {mode: "grab-offset", inertia: true});
        makePanelResizable(this.stockGadgetEl, {minWidth: 400, minHeight: 300});
        attachSaveListener(this.stockGadgetEl, "stock-gadget");
    }

    // 6. News Gadget
    if (this.newsGadgetEl && this.newsHeaderEl) {
            makePanelDraggable(this.newsGadgetEl, this.newsHeaderEl, {mode: "grab-offset", inertia: true});
            makePanelResizable(this.newsGadgetEl, {minWidth: 300, minHeight: 400});
            attachSaveListener(this.newsGadgetEl, "news-gadget");
    }
  }

    // --- Logic Inits ---
  private initWeatherLogic(): void {
      if (this.weatherGadgetEl) this.weather = new WeatherGadget(this.weatherGadgetEl);
  }
  private initFilesLogic(): void {
      if (this.filesGadgetEl) this.files = new FilesGadget(this.filesGadgetEl);
  }
  private initClockLogic(): void {
      if (this.clockGadgetEl) this.clock = new ClockGadget(this.clockGadgetEl);
  }
  private initStockLogic() {
      if (this.stockGadgetEl) this.stock = new StockGadget(this.stockGadgetEl);
  }
  private initNewsLogic() {
        if (this.newsGadgetEl) this.news = new NewsGadget(this.newsGadgetEl);
  }

    // --- Behavior Inits (Refactored to use shared helper) ---
    private initWeatherBehavior(): void {
        if (this.weatherGadgetEl && this.weatherHeaderEl && this.weatherToggleBtn && this.backdrop) {
            bindStandardGadgetEvents(
                this.weatherGadgetEl,
                this.weatherHeaderEl,
                this.weatherToggleBtn,
                this.backdrop,
                "weather-gadget",
                () => void this.weather?.refresh(false)
            );
        }
    }

    private initFilesBehavior(): void {
        if (this.filesGadgetEl && this.filesHeaderEl && this.filesToggleBtn && this.backdrop) {
            bindStandardGadgetEvents(
                this.filesGadgetEl,
                this.filesHeaderEl,
                this.filesToggleBtn,
                this.backdrop,
                "files-gadget",
                () => this.files?.refresh()
            );
        }
    }

    private initClockBehavior(): void {
        if (this.clockGadgetEl && this.clockHeaderEl && this.clockToggleBtn && this.backdrop) {
            bindStandardGadgetEvents(
                this.clockGadgetEl,
                this.clockHeaderEl,
                this.clockToggleBtn,
                this.backdrop,
                "clock-gadget"
            );
        }
    }

    private initStockBehavior(): void {
        if (this.stockGadgetEl && this.stockHeaderEl && this.stockToggleBtn && this.backdrop) {
            bindStandardGadgetEvents(
                this.stockGadgetEl,
                this.stockHeaderEl,
                this.stockToggleBtn,
                this.backdrop,
                "stock-gadget"
            );
        }
    }

    private initNewsBehavior() {
        if (this.newsGadgetEl && this.newsHeaderEl && this.newsToggleBtn && this.backdrop) {
            bindStandardGadgetEvents(
                this.newsGadgetEl,
                this.newsHeaderEl,
                this.newsToggleBtn,
                this.backdrop,
                "news-gadget"
            );
        }
    }
}