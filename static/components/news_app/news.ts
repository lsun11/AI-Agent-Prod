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

export class NewsGadget {
    private root: HTMLElement;
    private listEl: HTMLElement | null;
    private tickerEl: HTMLElement | null;
    private activeCategory: string = "tech";
    private cache: Record<string, Article[]> = {};

    // ✅ NEW: properties for cycling headlines
    private headlines: string[] = [];
    private currentHeadlineIdx = 0;
    private tickerInterval: number | null = null;

    constructor(root: HTMLElement) {
        this.root = root;
        this.listEl = root.querySelector("#news-list");
        this.tickerEl = root.querySelector("#news-ticker-text");

        const tabs = root.querySelectorAll(".news-tab");
        tabs.forEach(btn => {
            btn.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                btn.classList.add("active");
                const cat = btn.getAttribute("data-category");
                if (cat) this.loadCategory(cat);
            });
        });

        this.loadCategory("tech");
    }

    private async loadCategory(category: string) {
        this.activeCategory = category;
        if (!this.listEl) return;

        this.listEl.innerHTML = `<div class="news-loading">Searching web for ${category} news...</div>`;

        if (this.cache[category]) {
            this.renderList(this.cache[category]);
            return;
        }

        try {
            const res = await fetch(`/news?category=${category}`);
            if (!res.ok) throw new Error("Failed to fetch news");

            const data: NewsResponse = await res.json();
            this.cache[category] = data.articles;

            this.renderList(data.articles);

        } catch (err) {
            console.error(err);
            this.listEl.innerHTML = `<div class="news-loading" style="color:red">Failed to load news.</div>`;
            this.updateTicker([], true); // Clear ticker on error
        }
    }

    private renderList(articles: Article[]) {
        if (!this.listEl) return;
        this.listEl.innerHTML = "";

        // 1. Collect Headlines for the Ticker
        const headlines = articles.map(a => a.headline);
        this.updateTicker(headlines);

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
            this.listEl!.appendChild(item);
        });
    }

    // ✅ NEW: Cycle headlines with Fade Effect
    private updateTicker(headlines: string[], error = false) {
        if (!this.tickerEl) return;

        // Clear previous interval
        if (this.tickerInterval) {
            window.clearInterval(this.tickerInterval);
            this.tickerInterval = null;
        }

        if (error || headlines.length === 0) {
            this.tickerEl.textContent = error ? "News Unavailable" : "No headlines";
            this.tickerEl.classList.add("visible");
            return;
        }

        this.headlines = headlines;
        this.currentHeadlineIdx = 0;

        // Function to show the current headline
        const showCurrent = () => {
            if (!this.tickerEl) return;

            // 1. Fade Out
            this.tickerEl.classList.remove("visible");

            // 2. Wait for fade out (500ms), then swap text and Fade In
            setTimeout(() => {
                if (!this.tickerEl) return;
                // @ts-ignore
                this.tickerEl.textContent = this.headlines[this.currentHeadlineIdx];
                this.tickerEl.classList.add("visible");

                // Prepare next index
                this.currentHeadlineIdx = (this.currentHeadlineIdx + 1) % this.headlines.length;
            }, 500);
        };

        // Show first immediately
        showCurrent();

        // Cycle every 5 seconds
        this.tickerInterval = window.setInterval(showCurrent, 5000);
    }
}