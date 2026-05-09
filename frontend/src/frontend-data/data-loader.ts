import routeNames from "../frontend-data/route_names.json";
import routeDirs from "../frontend-data/route_dirs.json";
import type { WeatherType } from "../interfaces/enum-types";
export const ROUTE_NAMES_LIST: [number, string][] = Object.entries(routeNames).map(e => [Number(e[0]), e[1]]);
export const ROUTE_NAMES_REC = Object.fromEntries(Object.entries(routeNames)
                            .map(e => [Number(e[0]), e[1]])) as Record<number, string>;
export const ROUTE_DIRS_REC = Object.fromEntries(Object.entries(routeDirs)
                            .map(e => [Number(e[0]), e[1].map(dc => dc[0])])) as Record<number, string[]>;
// ROUTE_DIRS_REC extracts out a record of bus route (number): top 3 directions (string[1-3])

export const WEATHER_NAMES = Object.fromEntries([
    ["clear", "Clear"], ["cloudy","Cloudy"], ["dusty", "Windy or Dusty"], ["fog", "Fog"],
    ["previous", "Recently rained/snowed"], ["snow", "Snow"], ["rain", "Rain"], ["mixed", "Stormy or Mixed"]
]) as Record<WeatherType, string>
