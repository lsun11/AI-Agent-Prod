export declare function formatUtcOffsetLabel(timeZone: string): string;
export type ReverseGeocodeResponse = {
    name?: string;
    admin1?: string;
    country?: string;
    country_code?: string;
    timezone?: string;
};
export declare function buildPlaceLabel(geo: ReverseGeocodeResponse | null, fallbackLat: number, fallbackLon: number): string;
export type WeatherTexture = "clear" | "cloudy" | "fog" | "drizzle" | "rain" | "snow" | "thunderstorm" | "mixed";
export declare function weatherCodeToTexture(code: number | undefined | null): WeatherTexture;
//# sourceMappingURL=weather_helpers.d.ts.map