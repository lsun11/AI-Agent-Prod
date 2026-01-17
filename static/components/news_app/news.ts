// static/components/news_app/news.ts
interface Article {
    headline: string;
    summary: string;
    source: string;
    url: string;
    date: string;
}

interface NewsResponse {
    category: string;
    articles: Article[];
}

// ✅ NEW: Complex Category Structure
const CATEGORIES_COMPLEX: Record<string, string[]> = {
    "tech": ["AI", "industry", "others"],
    "sports": ["soccer", "basketball", "tennis", "football", "others"],
    "science": ["physics", "biology", "astronomy", "geography", "others"],
};

const REFRESH_MS = 4 * 60 * 60 * 1000; // 4 Hours

export class NewsGadget {
    private root: HTMLElement;
    private listEl: HTMLElement | null;
    private tickerEl: HTMLElement | null;
    private footerEl: HTMLElement | null;
    private subTabsContainer: HTMLElement | null; // ✅ New container

    // State
    private activeMain: string = "tech";
    private activeSub: string = "AI";

    // Cache keys will now be "main:sub" (e.g. "tech:AI")
    private memCache: Record<string, Article[]> = {};
    private currentArticles: Article[] = [];
    private currentHeadlineIdx = 0;
    private tickerInterval: number | null = null;
    private refreshTimer: number | null = null;

    constructor(root: HTMLElement) {
        this.root = root;
        this.listEl = root.querySelector("#news-list");
        this.tickerEl = root.querySelector("#news-ticker-text");
        this.footerEl = root.querySelector(".news-footer");

        // ✅ Create the Sub-Tabs Container dynamically if it doesn't exist in HTML
        // Insert it right after the main header/tabs
        let existingSub = root.querySelector(".news-sub-tabs");
        if (!existingSub) {
            this.subTabsContainer = document.createElement("div");
            this.subTabsContainer.className = "news-sub-tabs";
            // Insert after the header (assuming .gadget-header or .news-tabs exists)
            const header = root.querySelector(".news-tabs") || root.querySelector(".gadget-header");
            if (header && header.parentNode) {
                header.parentNode.insertBefore(this.subTabsContainer, header.nextSibling);
            }
        } else {
            this.subTabsContainer = existingSub as HTMLElement;
        }

        // Setup Main Tabs
        const tabs = root.querySelectorAll(".news-tab");
        tabs.forEach(btn => {
            btn.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                btn.classList.add("active");
                const cat = btn.getAttribute("data-category");
                if (cat && CATEGORIES_COMPLEX[cat]) {
                    this.switchMainTab(cat);
                }
            });
        });

        // Initial Load
        this.switchMainTab("tech");
        this.startAutoRefresh();
    }

    private startAutoRefresh() {
        if (this.refreshTimer) clearInterval(this.refreshTimer);
        this.refreshTimer = window.setInterval(() => {
            console.log(`[NewsGadget] Auto-refreshing ALL categories...`);
            this.refreshAllCategories(true);
        }, REFRESH_MS);
    }

    // ✅ Switch Main Category -> Render Sub-Tabs
    private switchMainTab(mainCat: string) {
        this.activeMain = mainCat;
        const subCats = CATEGORIES_COMPLEX[mainCat];

        // Render Sub-Category Pills
        if (this.subTabsContainer) {
            this.subTabsContainer.innerHTML = "";
            // @ts-ignore
            subCats.forEach((sub, index) => {
                const btn = document.createElement("button");
                btn.className = "news-sub-tab";
                btn.textContent = sub;
                btn.onclick = () => {
                    this.switchSubTab(mainCat, sub);
                    // Update active styling
                    this.subTabsContainer?.querySelectorAll(".news-sub-tab").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                };

                // Auto-select first sub-category
                if (index === 0) {
                    btn.classList.add("active");
                    this.activeSub = sub;
                }
                // @ts-ignore
                this.subTabsContainer.appendChild(btn);
            });
        }

        // Load the first sub-category by default
        // @ts-ignore
        this.switchSubTab(mainCat, subCats[0]);
    }

    // ✅ Switch Sub Category -> Fetch Data
    private switchSubTab(main: string, sub: string) {
        this.activeMain = main;
        this.activeSub = sub;
        const cacheKey = `${main}:${sub}`;

        const data = this.memCache[cacheKey] || [];

        // 1. Try Memory/Disk Cache first
        if (data.length === 0) {
             const diskData = this.getLocalData(cacheKey);
             if (diskData.length > 0) {
                 this.memCache[cacheKey] = diskData;
                 this.renderList(diskData);
                 this.updateTicker(diskData);
                 // Background refresh if needed?
                 // For now, if we found data, we trust it until auto-refresh hits.
             } else {
                 // No data at all -> Fetch immediately
                 this.fetchCategoryData(main, sub).then(() => {
                     // @ts-ignore
                     this.renderList(this.memCache[cacheKey]);
                     // @ts-ignore
                     this.updateTicker(this.memCache[cacheKey]);
                 });
             }
        } else {
            this.renderList(data);
            this.updateTicker(data);
        }
    }

    // ✅ Worker: Fetch specific Main + Sub combination
    private async fetchCategoryData(main: string, sub: string, forceRefresh = false) {
        const cacheKey = `${main}:${sub}`;

        // UI Loading State (only if active tab)
        if (this.activeMain === main && this.activeSub === sub && !forceRefresh) {
             if (this.listEl) this.listEl.innerHTML = `<div class="news-loading">Searching for ${sub} news...</div>`;
        }

        this.updateStatus(`Updating ${main} > ${sub}...`, true);

        try {
            // Construct query: "Tech AI" or "Sports Soccer"
            // The backend usually accepts a generic string.
            const queryParam = `${main} ${sub}`;

            const res = await fetch(`/news?category=${encodeURIComponent(queryParam)}`);
            if (!res.ok) throw new Error(`Failed to fetch ${queryParam}`);

            const data: NewsResponse = await res.json();

            // Update Caches
            this.memCache[cacheKey] = data.articles;
            this.saveLocalData(cacheKey, data.articles);

            this.updateStatus("Updated just now", false);

        } catch (err) {
            console.error(err);
            this.updateStatus("Update failed", false);
        }
    }

    // ✅ Loop through EVERYTHING (Heavy, but requested)
    private async refreshAllCategories(forceRefresh = false) {
        this.updateStatus("Updating all news...", true);

        // Flatten all combinations into a list of promises
        const tasks: Promise<void>[] = [];

        for (const [main, subs] of Object.entries(CATEGORIES_COMPLEX)) {
            for (const sub of subs) {
                // Add a small random delay to avoid hitting rate limits all at exact same ms
                const delay = Math.random() * 2000;
                const task = new Promise<void>(resolve => {
                    setTimeout(() => {
                        this.fetchCategoryData(main, sub, forceRefresh).then(resolve);
                    }, delay);
                });
                tasks.push(task);
            }
        }

        await Promise.all(tasks);

        // Re-render current view to show updates
        const currentKey = `${this.activeMain}:${this.activeSub}`;
        if (this.memCache[currentKey]) {
            this.renderList(this.memCache[currentKey]);
            this.updateTicker(this.memCache[currentKey]);
        }
    }

    // ... (Keep existing saveLocalData, getLocalData, updateStatus) ...
    // Note: getLocalData/saveLocalData keys should now handle the colon safely

    private saveLocalData(key: string, articles: Article[]) {
        try {
            localStorage.setItem(`news-cache-${key}`, JSON.stringify(articles));
        } catch (e) { }
    }

    private getLocalData(key: string): Article[] {
        try {
            const raw = localStorage.getItem(`news-cache-${key}`);
            return raw ? JSON.parse(raw) : [];
        } catch (e) { return []; }
    }

    // ... (Keep renderList and updateTicker exactly as before) ...
    private renderList(articles: Article[]) {
        if (!this.listEl) return;
        this.listEl.innerHTML = "";

        if (!articles || articles.length === 0) {
            this.listEl.innerHTML = `<div class="news-loading">No news found.</div>`;
            return;
        }

        const sorted = [...articles].sort((a, b) => {
            const dateA = new Date(a.date).getTime();
            const dateB = new Date(b.date).getTime();
            return (dateB || 0) - (dateA || 0);
        });

        const todayStr = new Date().toISOString().split('T')[0];

        sorted.forEach(art => {
            const isToday = art.date === todayStr;
            const badgeHtml = isToday ? `<span class="news-badge-new">NEW</span>` : ``;

            const item = document.createElement("div");
            item.className = "news-item";
            item.innerHTML = `
                <div class="news-header-row">
                    ${badgeHtml}
                    <a href="${art.url}" target="_blank" class="news-headline">${art.headline}</a>
                </div>
                <div class="news-summary">${art.summary}</div>
                <div class="news-meta">
                    <span class="news-source">${art.source}</span>
                    <span class="news-date">${art.date}</span>
                </div>
            `;
            this.listEl!.appendChild(item);
        });
    }

    // ... (Keep updateTicker exactly as before) ...
    private updateTicker(articles: Article[], error = false) {
        if (!this.tickerEl) return;
        if (JSON.stringify(this.currentArticles) === JSON.stringify(articles) && this.tickerInterval) return;
        if (this.tickerInterval) { clearInterval(this.tickerInterval); this.tickerInterval = null; }

        if (error || !articles || articles.length === 0) {
            this.tickerEl.innerHTML = `<div class="news-widget-headline">${error ? "Unavailable" : "Loading..."}</div>`;
            this.tickerEl.classList.add("visible");
            return;
        }

        this.currentArticles = articles;
        this.currentHeadlineIdx = 0;

        const showCurrent = () => {
            if (!this.tickerEl) return;
            this.tickerEl.classList.remove("visible");
            setTimeout(() => {
                if (!this.tickerEl) return;
                const art = this.currentArticles[this.currentHeadlineIdx];
                // @ts-ignore
                if (art) {
                    this.tickerEl.innerHTML = `
                    <div class="news-widget-headline">${art.headline}</div>
                    <div class="news-widget-meta">${art.source}</div>
                `;
                }
                this.tickerEl.classList.add("visible");
                this.currentHeadlineIdx = (this.currentHeadlineIdx + 1) % this.currentArticles.length;
            }, 500);
        };
        showCurrent();
        this.tickerInterval = window.setInterval(showCurrent, 6000);
    }

    // Helper for Status
    private updateStatus(msg: string, isLoading: boolean) {
        if (this.footerEl) {
            this.footerEl.textContent = msg;
            this.footerEl.style.color = isLoading ? "#ff4b2b" : "#adb5bd";
        }
        if (isLoading) this.root.classList.add("is-updating");
        else this.root.classList.remove("is-updating");
    }
}