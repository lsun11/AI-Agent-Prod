export declare class ClockGadget {
    private root;
    private mainTimeEl;
    private mainLocEl;
    private mainDateEl;
    private heroTimeEl;
    private heroDateEl;
    private heroLocEl;
    private gridEl;
    private earthCanvas;
    private earthCtx;
    private earthMarker;
    private timer;
    private coords;
    constructor(root: HTMLElement);
    private tick;
    private renderWorldGrid;
    private drawEarth;
    private initLocation;
    private reverseGeocode;
    private updateLocText;
}
//# sourceMappingURL=clock.d.ts.map