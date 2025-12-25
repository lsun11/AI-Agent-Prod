// static/chat-ui.ts
import {DROPDOWN_OPTIONS_BY_ID} from "../../constants/configs.js";
import type {SelectOption} from "../../constants/configs.js";
import {markdownToHtml} from "../../constants/markdown.js";
import {
    mapLanguageValue,
    translateLabel,
    getGreetingText,
    getFollowupText,
    applyInterfaceLanguage, refreshDropdownLabels
} from "../../constants/language.js";
import {
    extractWebsiteUrl,
    splitReplyIntoBubbles,
    createCompanyBubbleElement,
    createDownloadButtonElement,
    type CompanyVisual,
} from "./chat-helpers.js";
import type {Sender, LanguageCode} from "../../constants/types.js";
import {setHistoryHeaderLanguage} from "./history.js";

interface SuggestionsApiResponse {
    suggestions: string[];
}

const STORAGE_KEYS = {
    language: "ai_research_language",
    model: "ai_research_model",
    humanization: "ai_research_humanization",
};


export class ChatUI {
    private form: HTMLFormElement;
    private input: HTMLInputElement;
    private messagesEl: HTMLDivElement;
    private submitButton: HTMLButtonElement;
    private deepBtn: HTMLButtonElement;
    private modelSelect: HTMLSelectElement;
    private humanizationSelect: HTMLSelectElement;
    private languageSelect: HTMLSelectElement;
    private deepButton: HTMLButtonElement | null = null;
    private deepThinkingEnabled = false;
    private currentSuggestionGrid: HTMLDivElement | null = null;
    private currentTopicKey: string | null = null;
    private isThinking = false;
    private language: LanguageCode = "Chn";
    private latestCompaniesVisual: CompanyVisual[] = [];

    // ✅ Window Management Properties
    private gadgetEl: HTMLElement;
    private headerEl: HTMLElement;
    private toggleBtnEl: HTMLElement;
    private backdropEl: HTMLElement;

    // for SSE if you want to close later
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private currentEventSource?: EventSource;

    constructor() {
        const formEl = document.getElementById("chat-form");
        const inputEl = document.getElementById("chat-input");
        const messagesEl = document.getElementById("messages");

        if (!(formEl instanceof HTMLFormElement)) {
            throw new Error("chat-form element not found or not a form");
        }
        if (!(inputEl instanceof HTMLInputElement)) {
            throw new Error("chat-input element not found or not an input");
        }
        if (!(messagesEl instanceof HTMLDivElement)) {
            throw new Error("messages element not found or not a div");
        }

        this.form = formEl;
        this.input = inputEl;
        this.messagesEl = messagesEl;

        const button = this.form.querySelector("button");
        if (!(button instanceof HTMLButtonElement)) {
            throw new Error("Submit button not found");
        }
        this.submitButton = button;

        // --- Deep Thinking Button Setup ---
        this.deepBtn = document.createElement("button");
        this.deepBtn.type = "button";
        this.deepBtn.id = "deep-thinking-btn";
        this.deepBtn.className = "deep-thinking-btn";
        this.deepBtn.textContent = this.language === 'Chn'? "深度思考" : "Deep Thinking";
        this.deepButton = this.deepBtn;

        if (this.submitButton.parentElement) {
            this.submitButton.parentElement.insertBefore(
                this.deepBtn,
                this.submitButton.previousSibling
            );
        }

        this.deepBtn.addEventListener("click", () => {
            this.deepThinkingEnabled = !this.deepThinkingEnabled;
            if (this.deepThinkingEnabled) {
                this.deepBtn.classList.add("active");
            } else {
                this.deepBtn.classList.remove("active");
            }
        });

        // --- Select Elements ---
        // ✅ Capture Window Elements
        this.gadgetEl = document.getElementById("ai-gadget") as HTMLElement;
        this.headerEl = document.getElementById("ai-gadget-header") as HTMLElement;
        this.toggleBtnEl = document.getElementById("ai-gadget-toggle") as HTMLElement;
        this.backdropEl = document.getElementById("gadget-backdrop") as HTMLElement;

        // Initialize Logic
        this.attachListeners();

        // ✅ Initialize Window Logic (Expand/Collapse)
        if (this.gadgetEl && this.headerEl && this.toggleBtnEl && this.backdropEl) {
            this.attachWindowListeners();
        }

        // dropdowns
        const languageSelectEl = this.addDropDown("language-select");
        if (!languageSelectEl) throw new Error("Failed to create Language Select");

        const modelSelectEl = this.addDropDown("model-select");
        if (!modelSelectEl) throw new Error("Failed to create model-select dropdown");

        const humanizationSelectEl = this.addDropDown("humanization");
        if (!humanizationSelectEl) throw new Error("Failed to create humanization dropdown");

        this.languageSelect = languageSelectEl;
        this.modelSelect = modelSelectEl;
        this.humanizationSelect = humanizationSelectEl;

        this.restorePersistedSettings();

        this.language = mapLanguageValue(this.languageSelect.value);
        this.updateInterfaceLanguage();
        this.addGreeting(this.language);
        this.fetchSuggestions("fast").catch((err) =>
            console.error("Failed to fetch suggestions:", err)
        );
        setHistoryHeaderLanguage(this.language);

        // --- Settings Listeners ---
        this.languageSelect.addEventListener("change", () => {
            this.language = mapLanguageValue(this.languageSelect.value);
            try {
                window.localStorage.setItem(STORAGE_KEYS.language, this.languageSelect.value);
            } catch (err) {
                console.warn("Failed to persist language setting:", err);
            }

            this.updateInterfaceLanguage();
            refreshDropdownLabels(this.language);
            setHistoryHeaderLanguage(this.language);

            const switchedMsg =
                this.language === "Chn"
                    ? "🌐 已切换到中文界面"
                    : "🌐 Switched to English interface";
            this.addMessage(switchedMsg, "greeting");
            this.addGreeting(this.language);
            this.fetchSuggestions().catch((err) =>
                console.error("Failed to fetch suggestions:", err)
            );
        });

        this.modelSelect.addEventListener("change", () => {
            try {
                window.localStorage.setItem(STORAGE_KEYS.model, this.modelSelect.value);
            } catch (err) {
                console.warn("Failed to persist model setting:", err);
            }
        });

        this.humanizationSelect.addEventListener("change", () => {
            try {
                window.localStorage.setItem(STORAGE_KEYS.humanization, this.humanizationSelect.value);
            } catch (err) {
                console.warn("Failed to persist humanization setting:", err);
            }
        });
    }

    // =========================================================================
    // ✅ NEW: Window Management Logic (Replaces the inline script)
    // =========================================================================
    private attachWindowListeners(): void {
        // Toggle on Header Click
        this.headerEl.addEventListener("click", (e) => {
            if (e.target === this.toggleBtnEl) return; // Let button handle its own click
            this.toggleExpanded();
        });

        // Toggle on Button Click
        this.toggleBtnEl.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleExpanded();
        });

        // Close on Backdrop Click
        this.backdropEl.addEventListener("click", () => this.setExpanded(false));

        // Keyboard Accessibility
        this.headerEl.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                this.toggleExpanded();
            }
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") this.setExpanded(false);
        });
    }

    private toggleExpanded(): void {
        const isExpanded = this.gadgetEl.classList.contains("gadget--expanded");
        this.setExpanded(!isExpanded);
    }

    private setExpanded(expanded: boolean): void {
        this.gadgetEl.classList.toggle("gadget--expanded", expanded);
        this.gadgetEl.classList.toggle("gadget--collapsed", !expanded);
        this.backdropEl.classList.toggle("visible", expanded);

        this.gadgetEl.setAttribute("aria-expanded", expanded ? "true" : "false");
        this.toggleBtnEl.textContent = expanded ? "Close" : "Open";

        // Prevent scrolling on body when expanded
        document.documentElement.classList.toggle("no-scroll", expanded);
        document.body.classList.toggle("no-scroll", expanded);

        // 🐛 BUG FIX: Explicitly remove inline styles (width/height/transform) when collapsing
        // This prevents the "ellipse" issue where expanded dimensions persist on the collapsed sphere.
        if (!expanded) {
            this.gadgetEl.style.removeProperty("width");
            this.gadgetEl.style.removeProperty("height");
            this.gadgetEl.style.removeProperty("transform");
            this.gadgetEl.style.removeProperty("inset");
        }
    }
    // =========================================================================

    private restorePersistedSettings(): void {
        try {
            const savedLanguage = window.localStorage.getItem(STORAGE_KEYS.language);
            const savedModel = window.localStorage.getItem(STORAGE_KEYS.model);
            const savedHumanization = window.localStorage.getItem(STORAGE_KEYS.humanization);

            if (savedLanguage && this.languageSelect) {
                const option = Array.from(this.languageSelect.options).find((opt) => opt.value === savedLanguage);
                if (option) this.languageSelect.value = savedLanguage;
            }
            if (savedModel && this.modelSelect) {
                const option = Array.from(this.modelSelect.options).find((opt) => opt.value === savedModel);
                if (option) this.modelSelect.value = savedModel;
            }
            if (savedHumanization && this.humanizationSelect) {
                const option = Array.from(this.humanizationSelect.options).find((opt) => opt.value === savedHumanization);
                if (option) this.humanizationSelect.value = savedHumanization;
            }
        } catch (err) {
            console.warn("Failed to restore persisted settings:", err);
        }
    }

    private async fetchSuggestions(mode: string = "slow"): Promise<void> {
        const params = new URLSearchParams({language: this.language, mode: mode});
        const res = await fetch(`/suggestions?${params.toString()}`, {method: "GET"});

        if (!res.ok) {
            console.warn("Suggestions request failed:", res.statusText);
            return;
        }

        const data: SuggestionsApiResponse = await res.json();
        if (!data.suggestions || !Array.isArray(data.suggestions)) return;

        if (this.currentSuggestionGrid) {
            this.currentSuggestionGrid.remove();
            this.currentSuggestionGrid = null;
        }

        const grid = document.createElement("div");
        grid.className = "suggestion-grid";
        this.currentSuggestionGrid = grid;
        this.messagesEl.appendChild(grid);

        data.suggestions.forEach((q) => {
            if (typeof q === "string" && q.trim()) {
                this.addSuggestionBubble(q.trim(), grid);
            }
        });

        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }

    private addSuggestionBubble(text: string, grid: HTMLDivElement): void {
        const div = document.createElement("div");
        div.className = "message suggestion";
        div.textContent = text;
        div.addEventListener("click", () => {
            this.input.value = text;
            this.input.focus();
        });
        grid.appendChild(div);
    }

    private updateInterfaceLanguage(): void {
        const titleEl = document.getElementById("app-title");
        applyInterfaceLanguage(this.language, this.input, this.submitButton, this.deepBtn, titleEl);
    }

    private addGreeting(language: LanguageCode): void {
        const greeting = getGreetingText(language);
        this.addMessage(greeting, "greeting");
    }

    private addFollowupMsg(): void {
        const followup = getFollowupText(this.language);
        this.addMessage(followup, "greeting");
    }

    private attachListeners(): void {
        this.form.addEventListener("submit", (event: SubmitEvent) => {
            event.preventDefault();
            void this.handleSubmit();
        });
    }

    private addMessage(text: string, sender: Sender, url?: string): void {
        const div = document.createElement("div");
        div.className = `message ${sender}`;
        div.innerHTML = markdownToHtml(text);

        if (sender === "bot" && url) {
            div.classList.add("clickable");
            div.addEventListener("click", () => {
                window.open(url, "_blank");
            });
        }

        this.messagesEl.appendChild(div);
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }

    private addDropDown(selectId: string): HTMLSelectElement | null {
        const dropdownContainer = document.getElementById("dropdown-container");
        if (!dropdownContainer) return null;

        const options: SelectOption[] | undefined = DROPDOWN_OPTIONS_BY_ID[selectId];
        if (!options) return null;

        const select = document.createElement("select");
        select.id = selectId;
        select.className = selectId;

        for (const opt of options) {
            const optionEl = document.createElement("option");
            optionEl.value = opt.value;
            optionEl.dataset.labelKey = opt.label;
            optionEl.textContent = translateLabel(opt.label, this.language);
            if (opt.disabled) optionEl.disabled = true;
            if (opt.selected) optionEl.selected = true;
            select.appendChild(optionEl);
        }

        dropdownContainer.appendChild(select);
        return select;
    }

    private startThinking(): void {
        if (this.isThinking) return;
        this.isThinking = true;
        document.body.classList.add("thinking");
    }

    private stopThinking(): void {
        if (!this.isThinking) return;
        this.isThinking = false;
        document.body.classList.remove("thinking");
    }

    private updateTitle(topicLabel: string): void {
        const titleEl = document.getElementById("app-title");
        if (titleEl) {
            titleEl.textContent = `AI Research Assistant — ${topicLabel}`;
        }
        document.title = `AI Research: ${topicLabel}`;
    }

    private updateBackground(topicKey: string): void {
        if (this.currentTopicKey) {
            document.body.classList.remove(`topic-bg-${this.currentTopicKey}`);
        }
        document.body.classList.add(`topic-bg-${topicKey}`);
        this.currentTopicKey = topicKey;
    }

    private async handleSubmit(): Promise<void> {
        const text = this.input.value.trim();
        if (!text) return;

        this.addMessage(text, "user");
        this.input.value = "";
        this.input.focus();
        this.submitButton.disabled = true;
        if (this.deepButton) this.deepButton.disabled = true;

        try {
            const model = this.modelSelect.value || "gpt-4.1-mini";
            const temperature = this.humanizationSelect.value || "0.1";
            const mode = this.deepThinkingEnabled ? "deep" : "fast";
            const params = new URLSearchParams({message: text, model, temperature, mode});

            const es = new EventSource(`/chat_stream?${params.toString()}`);
            this.currentEventSource = es;

            const thinkingMsg = this.language === "Chn"
                ? "🤔 正在思考，请稍候…（大约需要0.5-3分钟）"
                : "🤔 Start thinking, please wait... (it takes approx 0.5-3 min.)";
            this.addMessage(thinkingMsg, "greeting");

            es.onmessage = (event: MessageEvent) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === "topic") {
                        this.updateTitle(data.topic_label);
                        this.updateBackground(data.topic_domain);
                        this.startThinking();
                        return;
                    }

                    if (data.type === "log") {
                        this.addMessage(data.message, "thinking");
                        return;
                    }

                    if (data.type === "final") {
                        const bubbles = splitReplyIntoBubbles(data.reply);
                        this.latestCompaniesVisual = (data.companies_visual || []) as CompanyVisual[];

                        for (let i = 0; i < bubbles.length; i++) {
                            const isFirst = i === 0;
                            const isLast = i === bubbles.length - 1;

                            if (!isFirst && !isLast) {
                                const companyIndex = i - 1;
                                const company = this.latestCompaniesVisual[companyIndex];
                                if (company) {
                                    // @ts-ignore
                                    const bubbleEl = createCompanyBubbleElement(bubbles[i], company);
                                    this.messagesEl.appendChild(bubbleEl);
                                    this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
                                } else {
                                    // @ts-ignore
                                    const url = extractWebsiteUrl(bubbles[i]);
                                    // @ts-ignore
                                    this.addMessage(bubbles[i], "bot", url);
                                }
                                continue;
                            }
                            const style = "bot-first";
                            // @ts-ignore
                            const url = extractWebsiteUrl(bubbles[i]);
                            // @ts-ignore
                            this.addMessage(bubbles[i], style as Sender, url);
                        }

                        if (data.download_pdf_url || data.download_docx_url || data.download_txt_url) {
                            const object = this.language === "Eng" ? "document" : "文档";
                            const el = createDownloadButtonElement(
                                {
                                    pdf: data.download_pdf_url,
                                    docx: data.download_docx_url,
                                    txt: data.download_txt_url
                                },
                                object,
                                this.language,
                                true
                            );
                            this.messagesEl.appendChild(el);
                            this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
                        }

                        if (data.slides_download_url) {
                            const object = this.language === "Eng" ? "slides" : "演示文稿";
                            const el = createDownloadButtonElement(
                                data.slides_download_url,
                                object,
                                this.language
                            );
                            this.messagesEl.appendChild(el);
                            this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
                        }

                        es.close();
                        this.stopThinking();
                        this.addFollowupMsg();
                        this.fetchSuggestions().catch((err) => console.error("Failed to fetch suggestions:", err));
                        this.submitButton.disabled = false;
                        if (this.deepButton) this.deepButton.disabled = false;
                    }

                } catch (e) {
                    console.error("Error parsing SSE data", e, event.data);
                }
            };

            es.onerror = (err) => {
                console.error("SSE error:", err);
                this.addMessage("Error: connection lost.", "bot");
                es.close();
                this.submitButton.disabled = false;
                if (this.deepButton) this.deepButton.disabled = false;
            };
        } catch (error) {
            console.error(error);
            const msg = error instanceof Error ? error.message : String(error);
            this.addMessage(`Network error: ${msg}`, "bot");
            this.submitButton.disabled = false;
            if (this.deepButton) this.deepButton.disabled = false;
        }
    }
}