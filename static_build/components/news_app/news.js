// static/components/news_app/news.ts
// ✅ 4 Hours in milliseconds
const REFRESH_MS = 4 * 60 * 60 * 1000;
export class NewsGadget {
    constructor(root) {
        this.activeCategory = "tech";
        this.cache = {};
        this.currentArticles = [];
        this.currentHeadlineIdx = 0;
        this.tickerInterval = null;
        // ✅ Timer reference
        this.refreshTimer = null;
        this.root = root;
        this.listEl = root.querySelector("#news-list");
        this.tickerEl = root.querySelector("#news-ticker-text");
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
        // ✅ Start Auto-Refresh Timer
        this.startAutoRefresh();
    }
    startAutoRefresh() {
        if (this.refreshTimer)
            clearInterval(this.refreshTimer);
        this.refreshTimer = window.setInterval(() => {
            console.log(`[NewsGadget] Auto-refreshing ${this.activeCategory} news...`);
            // Pass true to ignore cache and fetch fresh data
            this.loadCategory(this.activeCategory, true);
        }, REFRESH_MS);
    }
    // ✅ UPDATED: Added forceRefresh parameter
    async loadCategory(category, forceRefresh = false) {
        this.activeCategory = category;
        if (!this.listEl)
            return;
        // Show loading state
        this.listEl.innerHTML = `<div class="news-loading">Searching web for ${category} news...</div>`;
        // Check Cache (Skip if forcing refresh)
        if (!forceRefresh && this.cache[category]) {
            this.renderList(this.cache[category]);
            // Ensure ticker is updated even on cache hit
            this.updateTicker(this.cache[category]);
            return;
        }
        try {
            const res = await fetch(`/news?category=${category}`);
            if (!res.ok)
                throw new Error("Failed to fetch news");
            const data = await res.json();
            // Update Cache
            this.cache[category] = data.articles;
            this.renderList(data.articles);
            this.updateTicker(data.articles);
        }
        catch (err) {
            console.error(err);
            this.listEl.innerHTML = `<div class="news-loading" style="color:red">Failed to load news.</div>`;
            this.updateTicker([], true);
        }
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
            }, 1000);
        };
        showCurrent();
        this.tickerInterval = window.setInterval(showCurrent, 6000);
    }
}
//# sourceMappingURL=news.js.map