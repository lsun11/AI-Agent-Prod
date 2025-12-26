export declare class NewsGadget {
    private root;
    private listEl;
    private tickerEl;
    private activeCategory;
    private cache;
    private currentArticles;
    private currentHeadlineIdx;
    private tickerInterval;
    private refreshTimer;
    constructor(root: HTMLElement);
    private startAutoRefresh;
    private loadCategory;
    private renderList;
    private updateTicker;
}
//# sourceMappingURL=news.d.ts.map