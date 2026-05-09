import routeNames from "../frontend-data/route_names.json";
import routeDirs from "../frontend-data/route_dirs.json";
export const ROUTE_NAMES_LIST: [number, string][] = Object.entries(routeNames).map(e => [Number(e[0]), e[1]]);
export const ROUTE_DIRS_REC = Object.fromEntries(Object.entries(routeDirs)
                            .map(e => [Number(e[0]), e[1].map(dc => dc[0])])) as Record<number, string[]>;
// ROUTE_DIRS_REC extracts out a record of bus route (number): top 3 directions (string[1-3])
