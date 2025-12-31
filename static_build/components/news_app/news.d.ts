export declare class NewsGadget {
    private root;
    private listEl;
    private tickerEl;
    private footerEl;
    private activeCategory;
    private memCache;
    private currentArticles;
    private currentHeadlineIdx;
    private tickerInterval;
    private refreshTimer;
    constructor(root: HTMLElement);
    private startAutoRefresh;
    private refreshAllCategories;
    private switchTab;
    private fetchCategoryData;
    private saveLocalData;
    private getLocalData;
    private updateStatus;
    private renderList;
    private updateTicker;
}
//# sourceMappingURL=news.d.ts.map