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

const REFRESH_MS = 4 * 60 * 60 * 1000; // 4 Hours
const CATEGORIES = ["tech", "sports", "science"]; // ✅ Defined categories

export class NewsGadget {
    private root: HTMLElement;
    private listEl: HTMLElement | null;
    private tickerEl: HTMLElement | null;
    private footerEl: HTMLElement | null;

    private activeCategory: string = "tech";
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

        const tabs = root.querySelectorAll(".news-tab");
        tabs.forEach(btn => {
            btn.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                btn.classList.add("active");
                const cat = btn.getAttribute("data-category");
                if (cat) this.switchTab(cat);
            });
        });

        // ✅ Initial Load: Fetch ALL categories immediately on startup
        this.refreshAllCategories();

        // Start the timer
        this.startAutoRefresh();
    }

    private startAutoRefresh() {
        if (this.refreshTimer) clearInterval(this.refreshTimer);
        this.refreshTimer = window.setInterval(() => {
            console.log(`[NewsGadget] Auto-refreshing ALL categories...`);
            this.refreshAllCategories(true);
        }, REFRESH_MS);
    }

    // ✅ NEW: Refresh logic for ALL tabs
    private async refreshAllCategories(forceRefresh = false) {
        this.updateStatus("Updating all news...", true);

        // We use Promise.all to fetch them concurrently (or sequentially if you prefer)
        await Promise.all(CATEGORIES.map(cat => this.fetchCategoryData(cat, forceRefresh)));

        this.updateStatus("Updated just now", false);

        // After refreshing all, re-render the CURRENT tab to show changes
        this.renderList(this.memCache[this.activeCategory] || []);
        this.updateTicker(this.memCache[this.activeCategory] || []);
    }

    // ✅ Switch Tab: Just renders what we (hopefully) already have
    private switchTab(category: string) {
        this.activeCategory = category;
        const data = this.memCache[category] || [];

        // If data is missing (e.g. startup race condition), fetch it specifically
        if (data.length === 0) {
            this.fetchCategoryData(category).then(() => {
                // @ts-ignore
                this.renderList(this.memCache[category]);
                // @ts-ignore
                this.updateTicker(this.memCache[category]);
            });
        } else {
            this.renderList(data);
            this.updateTicker(data);
        }
    }

    // ✅ Worker: Fetches data for a specific category without touching the UI directly
    private async fetchCategoryData(category: string, forceRefresh = false) {
        // 1. Try LocalStorage if not forcing refresh
        if (!forceRefresh) {
            const cached = this.getLocalData(category);
            if (cached.length > 0) {
                this.memCache[category] = cached;
                // If this is the active tab, render immediately so user sees SOMETHING
                if (this.activeCategory === category) {
                    this.renderList(cached);
                    this.updateTicker(cached);
                }
                // If we found data and aren't forcing, we can stop here (optional)
                // But typically on "Restart", you want to fetch fresh anyway?
                // If you want "Stale-While-Revalidate", continue below.
            }
        }

        try {
            const res = await fetch(`/news?category=${category}`);
            if (!res.ok) throw new Error(`Failed to fetch ${category}`);

            const data: NewsResponse = await res.json();

            // Update Caches
            this.memCache[category] = data.articles;
            this.saveLocalData(category, data.articles);

        } catch (err) {
            console.error(err);
        }
    }

    private saveLocalData(category: string, articles: Article[]) {
        try {
            localStorage.setItem(`news-cache-${category}`, JSON.stringify(articles));
        } catch (e) { console.warn("Quota exceeded", e); }
    }

    private getLocalData(category: string): Article[] {
        if (this.memCache[category]) return this.memCache[category];
        try {
            const raw = localStorage.getItem(`news-cache-${category}`);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) {
                    return parsed;
                }
            }
        } catch (e) {}
        return [];
    }

    private updateStatus(msg: string, isLoading: boolean) {
        if (this.footerEl) {
            this.footerEl.textContent = msg;
            this.footerEl.style.color = isLoading ? "#ff4b2b" : "#adb5bd";
        }
        if (isLoading) {
            this.root.classList.add("is-updating");
        } else {
            this.root.classList.remove("is-updating");
        }
    }

    private renderList(articles: Article[]) {
        if (!this.listEl) return;
        this.listEl.innerHTML = "";

        if (!articles || articles.length === 0) {
            this.listEl.innerHTML = `<div class="news-loading">Searching web...</div>`;
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

    private updateTicker(articles: Article[], error = false) {
        if (!this.tickerEl) return;

        if (JSON.stringify(this.currentArticles) === JSON.stringify(articles) && this.tickerInterval) {
            return;
        }

        if (this.tickerInterval) {
            window.clearInterval(this.tickerInterval);
            this.tickerInterval = null;
        }

        if (error || !articles || articles.length === 0) {
            this.tickerEl.innerHTML = `<div class="news-widget-headline">${error ? "News Unavailable" : "Loading..."}</div>`;
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
                if (art) {
                    this.tickerEl.innerHTML = `
                    <div class="news-widget-headline">${art.headline}</div>
                    <div class="news-widget-meta">${art.source} • ${art.date}</div>
                `;
                }

                this.tickerEl.classList.add("visible");
                this.currentHeadlineIdx = (this.currentHeadlineIdx + 1) % this.currentArticles.length;
            }, 500);
        };

        showCurrent();
        this.tickerInterval = window.setInterval(showCurrent, 6000);
    }
}