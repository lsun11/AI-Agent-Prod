// static/components/news_app/news.ts
const REFRESH_MS = 4 * 60 * 60 * 1000;
export class NewsGadget {
    constructor(root) {
        this.activeCategory = "tech";
        // In-memory cache for switching tabs quickly without disk reads
        this.memCache = {};
        this.currentArticles = [];
        this.currentHeadlineIdx = 0;
        this.tickerInterval = null;
        this.refreshTimer = null;
        this.root = root;
        this.listEl = root.querySelector("#news-list");
        this.tickerEl = root.querySelector("#news-ticker-text");
        this.footerEl = root.querySelector(".news-footer"); // Ensure you have this class in HTML
        const tabs = root.querySelectorAll(".news-tab");
        tabs.forEach(btn => {
            btn.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                btn.classList.add("active");
                const cat = btn.getAttribute("data-category");
                if (cat)
                    this.loadCategory(cat);
            });
        });
        // Initial Load
        this.loadCategory("tech");
        this.startAutoRefresh();
    }
    startAutoRefresh() {
        if (this.refreshTimer)
            clearInterval(this.refreshTimer);
        this.refreshTimer = window.setInterval(() => {
            console.log(`[NewsGadget] Auto-refreshing ${this.activeCategory} news...`);
            this.loadCategory(this.activeCategory, true);
        }, REFRESH_MS);
    }
    async loadCategory(category, forceRefresh = false) {
        this.activeCategory = category;
        if (!this.listEl)
            return;
        // 1. Try to load from LocalStorage / Memory FIRST
        // This ensures the UI is never blank on reload
        const cachedArticles = this.getLocalData(category);
        if (cachedArticles.length > 0) {
            // Render cached data immediately
            this.renderList(cachedArticles);
            this.updateTicker(cachedArticles);
            // If we have valid data and NOT forcing refresh, stop here.
            // (Unless you want to always background-refresh on load, remove the second condition)
            if (!forceRefresh && this.memCache[category]) {
                return;
            }
        }
        else {
            // Only show full loading spinner if we have NOTHING to show
            this.listEl.innerHTML = `<div class="news-loading">Searching web for ${category} news...</div>`;
        }
        // 2. Show "Updating" status if we are keeping old data visible
        this.updateStatus("Updating...", true);
        try {
            // 3. Fetch Fresh Data
            const res = await fetch(`/news?category=${category}`);
            if (!res.ok)
                throw new Error("Failed to fetch news");
            const data = await res.json();
            // 4. Update UI & Caches with Fresh Data
            this.memCache[category] = data.articles;
            this.saveLocalData(category, data.articles);
            this.renderList(data.articles);
            this.updateTicker(data.articles);
            this.updateStatus("Updated just now", false);
        }
        catch (err) {
            console.error(err);
            // If we have no data at all, show error.
            // If we have stale data, keep showing it but warn in footer.
            if (this.listEl.childElementCount === 0 || this.listEl.querySelector(".news-loading")) {
                this.listEl.innerHTML = `<div class="news-loading" style="color:red">Failed to load news.</div>`;
                this.updateTicker([], true);
            }
            this.updateStatus("Update failed (Offline)", false);
        }
    }
    // ✅ HELPER: Save to Browser LocalStorage
    saveLocalData(category, articles) {
        try {
            localStorage.setItem(`news-cache-${category}`, JSON.stringify(articles));
        }
        catch (e) {
            console.warn("Quota exceeded", e);
        }
    }
    // ✅ HELPER: Load from Browser LocalStorage
    getLocalData(category) {
        // Try memory first
        if (this.memCache[category])
            return this.memCache[category];
        // Try disk
        try {
            const raw = localStorage.getItem(`news-cache-${category}`);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) {
                    this.memCache[category] = parsed; // Sync memory
                    return parsed;
                }
            }
        }
        catch (e) { }
        return [];
    }
    updateStatus(msg, isLoading) {
        if (!this.footerEl)
            return;
        this.footerEl.textContent = msg;
        this.footerEl.style.opacity = isLoading ? "0.7" : "0.4";
    }
    renderList(articles) {
        if (!this.listEl)
            return;
        this.listEl.innerHTML = "";
        if (articles.length === 0) {
            this.listEl.innerHTML = `<div class="news-loading">No news found.</div>`;
            return;
        }
        articles.forEach(art => {
            const item = document.createElement("div");
            item.className = "news-item";
            item.innerHTML = `
                <a href="${art.url}" target="_blank" class="news-headline">${art.headline}</a>
                <div class="news-summary">${art.summary}</div>
                <div class="news-meta">
                    <span class="news-source">${art.source}</span>
                    <span class="news-date">${art.date}</span>
                </div>
            `;
            this.listEl.appendChild(item);
        });
    }
    updateTicker(articles, error = false) {
        if (!this.tickerEl)
            return;
        // Don't reset if the content is exactly the same (prevents jitter)
        if (JSON.stringify(this.currentArticles) === JSON.stringify(articles) && this.tickerInterval) {
            return;
        }
        if (this.tickerInterval) {
            window.clearInterval(this.tickerInterval);
            this.tickerInterval = null;
        }
        if (error || articles.length === 0) {
            this.tickerEl.innerHTML = `<div class="news-widget-headline">${error ? "News Unavailable" : "No headlines"}</div>`;
            this.tickerEl.classList.add("visible");
            return;
        }
        this.currentArticles = articles;
        this.currentHeadlineIdx = 0;
        const showCurrent = () => {
            if (!this.tickerEl)
                return;
            this.tickerEl.classList.remove("visible");
            setTimeout(() => {
                if (!this.tickerEl)
                    return;
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
//# sourceMappingURL=news.js.map