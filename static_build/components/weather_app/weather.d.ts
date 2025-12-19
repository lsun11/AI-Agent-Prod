export declare class WeatherGadget {
    private gadget;
    private metaEl;
    private locEl;
    private iconEl;
    private tempEl;
    private descEl;
    private statsEl;
    private updatedEl;
    private detailsEl;
    private refreshBtn;
    private coords;
    private timer;
    constructor(gadget: HTMLElement);
    destroy(): void;
    private setMeta;
    private loadCachedCoords;
    private cacheCoords;
    private detectCoords;
    private buildForecastUrl;
    refresh(forcePrompt: boolean): Promise<void>;
}
//# sourceMappingURL=weather.d.ts.map