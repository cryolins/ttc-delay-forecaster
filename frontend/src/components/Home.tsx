import ParamInput from "./ParamInput";


function Home() {

    return (<div id="main-container">
        <div id="title-container">
            <h1 className="title w-full">TTC Delay Time Forecaster</h1>
            <h4 className="w-full">How long do incidents delay buses?</h4>
        </div>
        <ParamInput />
    </div>)
}

export default Home;