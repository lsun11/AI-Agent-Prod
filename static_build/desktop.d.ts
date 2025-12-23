export declare class Desktop {
    private gadget;
    private header;
    private toggleBtn;
    private backdrop;
    private weatherGadgetEl;
    private weatherHeaderEl;
    private weatherToggleBtn;
    private weather?;
    private filesGadgetEl;
    private filesHeaderEl;
    private filesToggleBtn;
    private files?;
    private clockGadgetEl;
    private clockHeaderEl;
    private clockToggleBtn;
    private clock?;
    private chatUI?;
    constructor();
    /**
     * Saves the current 'left' and 'top' coordinates to localStorage.
     */
    private savePosition;
    /**
     * Restores position from localStorage.
     * STRICTLY overrides CSS defaults (bottom/right/inset) to prevent jumping.
     */
    private restorePosition;
    private initComponents;
    private initGadgetBehavior;
    private initDraggables;
    private initWeatherLogic;
    private initWeatherBehavior;
    private initFilesLogic;
    private initFilesBehavior;
    private initClockLogic;
    private initClockBehavior;
}
//# sourceMappingURL=desktop.d.ts.map