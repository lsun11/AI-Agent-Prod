/**
 * IMPORTANT: This class MUST receive the weather gadget root element,
 * and query elements inside it (no document.getElementById) so multiple gadgets work.
 */
export declare class WeatherGadget {
    private root;
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
    private tzEl;
    private forecastEl;
    constructor(weatherGadgetRoot: HTMLElement);
    destroy(): void;
    private isExpanded;
    private setMeta;
    private setTitleOnceIfMissing;
    private loadCachedCoords;
    private cacheCoords;
    private reverseGeocode;
    private tryBrowserGeolocation;
    private tryGeoIpFallback;
    private getHardFallback;
    private detectCoords;
    private buildBackendWeatherUrl;
    refresh(forcePrompt: boolean): Promise<void>;
    private formatDow;
    private render7Day;
}
//# sourceMappingURL=weather.d.ts.map