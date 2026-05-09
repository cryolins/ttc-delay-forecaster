import type { DirectionType, IncidentType, WeatherType } from "./enum-types"

export type ResponseData<T> = {
    status: "success"
    content: T
}

export type ErrorResponse = {
    status: "error"
    message: string
}

export type APIResponseData<T> = ResponseData<T> | ErrorResponse;

export interface AdvancedOptions {
    incident_type: IncidentType
    weather_category: WeatherType
    temperature_2m: number
    precipitation: number
    windspeed_10m: number
    snowfall: number
}

export interface PredictRequest {
    route: number
    timestamp: string
    direction: DirectionType | null
    advanced: AdvancedOptions | null
}

export interface PredictResponse {
    route: number
    timestamp: string
    direction: DirectionType | null
    predicted_delay: number
    route_avg_delay: number
    route_entries: number
    weather_category: WeatherType
    temperature: number
    precipitation: number
    input_advanced: boolean
}

