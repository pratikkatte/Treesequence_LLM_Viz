import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Chatbot from "./components/Chatbot";
import Visualization from './components/visualization';
  
function App() {

  const [userName, setUserName] = useState("");


  return (
    <div className="app-container">
    <div className="not-supported-message">
      <p>This view is not supported on mobile devices. Please enable desktop mode.</p>
    </div>
        <div className="right-container">
          <Chatbot userName={userName} />
        </div>
        <div className="left-container">
            <Visualization/>
            {/* <div className="h-[calc(100%-4rem)]">
              <TaxoniumBit sourceData={sourceData} />
            </div> */}
        </div>
    </div>
  );
}

export default App
