import "./inputs.css";
import { ROUTE_DIRS_REC, ROUTE_NAMES_LIST } from "../frontend-data/data-loader";
import { useEffect, useState } from "react";
import { type APIResponseData, type PredictRequest, type PredictResponse } from "../interfaces/backend";
import { BACKEND_URL } from "../config";
import type { DirectionType } from "../interfaces/enum-types";
import DelayModal from "./DelayModal";

function ParamInput() {
  // setting initial states for inputs
  const mountTime = new Date();
  const [route, setRoute] = useState(7);
  const [direction, setDirection] = useState<DirectionType | "">("");
  const [dateStr, setDateStr] = useState(mountTime.toISOString().slice(0, 10));
  const [timeStr, setTimeStr] = useState(mountTime.toTimeString().slice(0, 5));
  const [predData, setPredData] = useState<PredictResponse>();
  const [isFetching, setIsFetching] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    // console.log(route);
    setDirection("");
  }, [route]);

  // action of see delay button press
  const handleSeeDelay = () => {
    // async function call to fetch data
    async function fetchPred() {
      const advancedOptions = null; // TODO for advanced options
      const payload: PredictRequest = {
        route: route,
        timestamp: `${dateStr}T${timeStr}`,
        direction: direction || null,
        advanced: advancedOptions
      }

      setIsFetching(true);
      // try to fetch
      try {
        const res = await fetch(`${BACKEND_URL}/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const resJson: APIResponseData<PredictResponse> = await res.json();

        if (resJson.status === "error") {
          setErrorMsg(resJson.message);
          console.error(res);
          setIsFetching(false);
          return;
        }

        setPredData(resJson.content);
        setErrorMsg("");
        setIsFetching(false);
        console.log(resJson.content);
      } catch (e) {
        setErrorMsg("Unknown error occurred. Please try again.");
        setIsFetching(false);
        console.error(e);
      }
    }

    // calling async function to fetch
    fetchPred();
  }

  return (<div className="rounded-card inputs-container">
    <div className="input-set w-full">

      {/* Route selector */}
      <div id="route-select-container" className="param-container">
        <label htmlFor="route-select" className="font-medium">Route</label>
        <select id="route-select" required value={route} onChange={(e) => setRoute(Number(e.currentTarget.value))}>
          {ROUTE_NAMES_LIST.map((v) =>
            <option key={`${v[0]}`} value={v[0]} className={`bg-${Math.floor(v[0] / 100) || 1}xx text-white`}
            >{`${v[0]} ${v[1]}`}</option>
          )}
        </select>
      </div>

      {/* direction selector */}
      <div id="direction-select-container" className="param-container">
        <label htmlFor="direction-select" className="font-medium">Direction</label>
        <select id="direction-select" required value={direction} onChange={(e) => setDirection(e.currentTarget.value as DirectionType | "")}>
          <option key={"N"} value={"N"} hidden={!ROUTE_DIRS_REC[route].includes("N")} className="option-frame">Northbound</option>
          <option key={"S"} value={"S"} hidden={!ROUTE_DIRS_REC[route].includes("S")} className="option-frame">Southbound</option>
          <option key={"W"} value={"W"} hidden={!ROUTE_DIRS_REC[route].includes("W")} className="option-frame">Westbound</option>
          <option key={"E"} value={"E"} hidden={!ROUTE_DIRS_REC[route].includes("E")} className="option-frame">Eastbound</option>
          <option key={"B"} value={"B"} hidden={!ROUTE_DIRS_REC[route].includes("B")} className="option-frame">Various</option>
          <option key={"A"} value={""} className="option-frame">Take Average</option>
        </select>
      </div>
      
      {/* date and time selectors */}
      <div className="input-set">
        <div className="param-container">
          <label htmlFor="date-input" className="font-medium">Date</label>
          <input type="date" id="date-input" value={dateStr} onChange={(e) => setDateStr(e.currentTarget.value)}/>
        </div>
        <div className="param-container">
          <label htmlFor="time-input" className="font-medium">Time</label>
          <input type="time" id="time-input" value={timeStr} onChange={(e) => setTimeStr(e.currentTarget.value)}/>
        </div>
      </div>
      
      {/* submit button */}
      <button className="delay-submit enforce-font" onClick={handleSeeDelay} disabled={isFetching}>
        {isFetching ? "Loading..." : "See delay"}
      </button>

      {/* delay info modal */}
      {predData && <DelayModal prediction={predData} closeModal={() => setPredData(undefined)} />}

    </div>
  </div>)
}

export default ParamInput;