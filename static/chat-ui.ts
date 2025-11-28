// static/chat-ui.ts
import {DROPDOWN_OPTIONS_BY_ID} from "./configs.js";
import type {SelectOption} from "./configs.js";
import {markdownToHtml} from "./markdown.js";
import {
    mapLanguageValue,
    translateLabel,
    getGreetingText,
    getFollowupText,
    applyInterfaceLanguage, refreshDropdownLabels
} from "./language.js";
import type {Sender, LanguageCode} from "./types.js";
import {RECOMMENDATION_STARTERS} from "./types.js";

interface SuggestionsApiResponse {
    suggestions: string[];
}


export class ChatUI {
    private form: HTMLFormElement;
    private input: HTMLInputElement;
    private messagesEl: HTMLDivElement;
    private submitButton: HTMLButtonElement;
    private modelSelect: HTMLSelectElement;
    private humanizationSelect: HTMLSelectElement;
    private languageSelect: HTMLSelectElement;
    private suggestionGrid: HTMLDivElement | null = null;
    private currentSuggestionGrid: HTMLDivElement | null = null;
    private currentTopicKey: string | null = null;
    private isThinking = false;
    private language: LanguageCode = "Chn";

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

        this.attachListeners();

        // dropdowns
        const languageSelectEl = this.addDropDown("language-select");
        if (!languageSelectEl) {
            throw new Error("Failed to create Language Select");
        }
        const modelSelectEl = this.addDropDown("model-select");
        if (!modelSelectEl) {
            throw new Error("Failed to create model-select dropdown");
        }
        const humanizationSelectEl = this.addDropDown("humanization");
        if (!humanizationSelectEl) {
            throw new Error("Failed to create humanization dropdown");
        }

        this.languageSelect = languageSelectEl;
        this.modelSelect = modelSelectEl;
        this.humanizationSelect = humanizationSelectEl;

        // language setup
        this.language = mapLanguageValue(this.languageSelect.value);
        this.updateInterfaceLanguage();
        this.addGreeting(this.language);
        this.fetchSuggestions("fast").catch((err) =>
            console.error("Failed to fetch suggestions:", err)
        );

        this.languageSelect.addEventListener("change", () => {
            this.language = mapLanguageValue(this.languageSelect.value);
            this.updateInterfaceLanguage();

            refreshDropdownLabels(this.language);

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
    }

    private async fetchSuggestions(mode: string = "slow"): Promise<void> {
        const params = new URLSearchParams({language: this.language, mode: mode});
        const res = await fetch(`/suggestions?${params.toString()}`, {method: "GET"});

        if (!res.ok) {
            console.warn("Suggestions request failed:", res.statusText);
            return;
        }

        const data: SuggestionsApiResponse = await res.json();
        if (!data.suggestions || !Array.isArray(data.suggestions)) {
            return;
        }

        if (this.currentSuggestionGrid) {
            this.currentSuggestionGrid.remove();
            this.currentSuggestionGrid = null;
        }

        const grid = document.createElement("div");
        grid.className = "suggestion-grid";
        this.currentSuggestionGrid = grid;

        // Append directly under the most recent message (which you just added)
        this.messagesEl.appendChild(grid);

        // Now add the suggestion bubbles into THIS grid
        data.suggestions.forEach((q) => {
            if (typeof q === "string" && q.trim()) {
                this.addSuggestionBubble(q.trim(), grid);
            }
        });

        // Scroll to bottom so the user sees them
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }


    private addSuggestionBubble(text: string, grid: HTMLDivElement): void {
        const div = document.createElement("div");
        div.className = "message suggestion";
        div.textContent = text;

        // Click to autofill input
        div.addEventListener("click", () => {
            this.input.value = text;
            this.input.focus();
        });

        grid.appendChild(div);
    }


    private updateInterfaceLanguage(): void {
        const titleEl = document.getElementById("app-title");
        applyInterfaceLanguage(this.language, this.input, this.submitButton, titleEl);
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

    private extractWebsiteUrl(text: string): string | undefined {
        const lines = text.split("\n");
        for (const line of lines) {
            const m1 = line.match(/Website[:：]\s*(https?:\/\/\S+)/i);
            const m2 = line.match(/网站[:：]\s*(https?:\/\/\S+)/i);
            const m = m1 || m2;
            if (m) {
                // @ts-ignore
                return m[1].trim().replace(/[)\]]+$/, "");
            }
        }
        return undefined;
    }

    private addMessage(text: string, sender: Sender, url?: string): void {
        const div = document.createElement("div");
        div.className = `message ${sender}`;

        // render markdown → HTML
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

    private addDownloadButton(url: string, object: string): void {
        // Create a NEW container for this answer's download button(s)
        const downloadContainer = document.createElement("div");
        downloadContainer.className = "download-container";

        const button = document.createElement("button");
        button.type = "button";
        button.className = "download-button";
        button.textContent =
            this.language === "Eng"
                ? "Download summary (" + object + ")"
                : "下载总结 (" + object + ")";

        button.addEventListener("click", () => {
            window.open(url, "_blank");
        });

        downloadContainer.appendChild(button);

        // Append THIS container right after the current answer's bubbles
        this.messagesEl.appendChild(downloadContainer);
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }


    private addDropDown(selectId: string): HTMLSelectElement | null {
        const dropdownContainer = document.getElementById("dropdown-container");
        if (!dropdownContainer) {
            console.error("dropdown-container not found");
            return null;
        }

        const options: SelectOption[] | undefined = DROPDOWN_OPTIONS_BY_ID[selectId];
        if (!options) {
            console.warn(`No dropdown options configured for selectId="${selectId}"`);
            return null;
        }

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

    private splitReplyIntoBubbles(reply: string): string[] {
        const lines = reply.split(/\r?\n/);
        const bubbles: string[] = [];
        let current: string[] = [];

        const flush = () => {
            const text = current.join("\n").trim();
            if (text) {
                bubbles.push(text);
            }
            current = [];
        };

        for (const rawLine of lines) {
            const line = rawLine;
            const trimmed = rawLine.trim();

            if (!trimmed && current.length === 0) continue;

            if (trimmed.startsWith("📊 Results for:")) {
                flush();
                current.push(line);
                continue;
            }

            if (/^\d+\.\s*🏢/.test(trimmed)) {
                flush();
                current.push(line);
                continue;
            }

            // if (trimmed.startsWith("**Recommendations") || trimmed.startsWith("**推荐"))
            if (RECOMMENDATION_STARTERS.some(starter => trimmed.startsWith(starter))) {
                flush();
                current.push(line);
                continue;
            }

            current.push(line);
        }

        flush();
        return bubbles;
    }

    private async handleSubmit(): Promise<void> {
        const text = this.input.value.trim();
        if (!text) return;

        this.addMessage(text, "user");
        this.input.value = "";
        this.input.focus();
        this.submitButton.disabled = true;

        try {
            const model = this.modelSelect.value || "gpt-4.1-mini";
            const temperature = this.humanizationSelect.value || "0.1";
            const params = new URLSearchParams({message: text, model, temperature});

            const es = new EventSource(`/chat_stream?${params.toString()}`);

            this.currentEventSource = es;

            const thinkingMsg =
                this.language === "Chn"
                    ? "🤔 正在思考，请稍候…"
                    : "🤔 Start thinking, please wait...";
            this.addMessage(thinkingMsg, "greeting");

            es.onmessage = (event: MessageEvent) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log("!!!!!!!", data.reply)
                    if (data.type === "topic") {
                        const topicLabel = data.topic_label as string;
                        const topicKey = data.topic_key as string;
                        this.updateTitle(topicLabel);
                        this.updateBackground(topicKey);
                        this.startThinking();
                        return;
                    }

                    if (data.type === "log") {
                        this.addMessage(data.message as string, "thinking");
                        return;
                    }

                    if (data.type === "final") {
                        const bubbles = this.splitReplyIntoBubbles(data.reply as string);
                        for (let i = 0; i < bubbles.length; i++) {
                            const style = i === 0 ? "bot-first" : i === bubbles.length - 1 ? "bot-first" : "bot";
                            // @ts-ignore
                            const url = this.extractWebsiteUrl(bubbles[i]);
                            // @ts-ignore
                            this.addMessage(bubbles[i], style, url);
                        }
                        if (data.download_url) {
                            const object = this.language === "Eng" ? "document" : "文档";
                            this.addDownloadButton(data.download_url as string, object);
                        }

                        if (data.slides_download_url) {
                            const object = this.language === "Eng" ? "slides" : "演示文稿";
                            this.addDownloadButton(data.slides_download_url as string, object);
                        }

                        es.close();
                        this.stopThinking();
                        this.addFollowupMsg();
                        this.fetchSuggestions().catch((err) =>
                            console.error("Failed to fetch suggestions:", err)
                        );
                        this.submitButton.disabled = false;
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
            };
        } catch (error) {
            console.error(error);
            const msg = error instanceof Error ? error.message : String(error);
            this.addMessage(`Network error: ${msg}`, "bot");
            this.submitButton.disabled = false;
        }
    }
}
