export declare class NewsGadget {
    private root;
    private listEl;
    private tickerEl;
    private footerEl;
    private subTabsContainer;
    private activeMain;
    private activeSub;
    private memCache;
    private currentArticles;
    private currentHeadlineIdx;
    private tickerInterval;
    private refreshTimer;
    constructor(root: HTMLElement);
    private startAutoRefresh;
    private switchMainTab;
    private switchSubTab;
    private fetchCategoryData;
    private refreshAllCategories;
    private saveLocalData;
    private getLocalData;
    private renderList;
    private updateTicker;
    private updateStatus;
}
//# sourceMappingURL=news.d.ts.map