import "./delay-modal.css"
import { LucideX } from "lucide-react";
import type { PredictResponse } from "../interfaces/backend"
import { ModalWrapper } from "./modals";
import { ROUTE_NAMES_REC, WEATHER_NAMES } from "../frontend-data/data-loader";

interface DelayModalProps{
  prediction: PredictResponse
  closeModal: () => void
}

function getDelayTimeClass(delayTime: number) {
  if (delayTime <= 10) { return "good"; }
  else if (delayTime <= 20) { return "neutral"; }
  return "bad";
}
function getDelayDiffClass(delayDiff: number) {
  if (delayDiff < 0) { return "good"; }
  else if (delayDiff <= 5) { return "neutral"; }
  return "bad";
}

function DelayModal({ prediction, closeModal }: DelayModalProps) {
  const predDate = new Date(prediction.timestamp);
  const isNight = predDate.getHours() < 6 || predDate.getHours() >= 18
  const imgName = (prediction.weather_category === "clear") ?
                  (isNight ? "clear-night" : "clear-day") : prediction.weather_category;
  const weatherName = WEATHER_NAMES[prediction.weather_category];
  const roundedPredDelay = Math.round(prediction.predicted_delay * 100) / 100;
  const roundedAvgDelay = Math.round(prediction.route_avg_delay * 100) / 100;
  const delayDiff = Math.round((roundedPredDelay - roundedAvgDelay) * 100) / 100;

  return (
    <ModalWrapper closeModal={closeModal}>
      <div id="delay-container" className="rounded-card" onClick={(e) => e.stopPropagation()}>
        <div id="delay-header">
          <div id="delay-info-container">
            <div id="delay-route-number" className={`bg-${Math.floor(prediction.route / 100) || 1}xx text-white`}>{prediction.route}</div>
            <div id="delay-key-info">
              <h4>{ROUTE_NAMES_REC[prediction.route]}</h4>
              <p>{predDate.toLocaleString()}</p>
            </div>
          </div>
          <button id="close-modal" onClick={closeModal}>
            <LucideX className="close-modal-x"/>
          </button>
        </div>

        <div id="weather-container">
          <img src={`/weather-iconset/${imgName}.svg`} alt={`weather: ${imgName}`} id="weather-img"/>
          <div id="weather-details">
            <h5>{weatherName}</h5>
            <p>{`${prediction.temperature}°C | ${prediction.precipitation}mm precipitation`}</p>
          </div>
        </div>

        <div id="time-container">
          <div id="pred-delay-container" className="delay-mins-container">
            Predicted Delay
            <h1 className={`text-${getDelayTimeClass((roundedPredDelay))}`}>{roundedPredDelay}m</h1>
          </div>

          <div id="other-delay-time-container">
            <div id="minor-delay-time-container">
              <div id="avg-delay-container" className="delay-mins-container">
                Route Avg Delay
                <h3 className={`text-${getDelayTimeClass(roundedAvgDelay)}`}>{roundedAvgDelay}m</h3>
              </div>
              <div id="diff-delay-container" className="delay-mins-container">
                Change From Avg
                <h3 className={`text-${getDelayDiffClass(delayDiff)}`}>{delayDiff > 0 ? "+" : ""}{delayDiff}m</h3>
              </div>
            </div>

            <p id="times-note">*when a delaying incident occurs</p>
          </div>

        </div>
      </div>
    </ModalWrapper>
  );
}

export default DelayModal