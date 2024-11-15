import React, { useState, Suspense, useRef, useEffect, useCallback } from "react";
import AboutOverlay from "./components/AboutOverlay";
import TaxoniumBit from "./components/TaxoniumBit";
import { getDefaultSearch } from "./utils/searchUtil.js";
import useQueryAsState from "./hooks/useQueryAsState";

import tracks from './tracks.jsx';
import assembly from './assembly.jsx';
import defaultSession from './defaultSession.jsx'
import addTrack  from './utils/TrackUtils.jsx'
import { Header } from './utils/UIUtils.jsx'
import FileUpload from './utils/uploadUtils.jsx'
import DashboardPlugin from './plugins'
import { FaArrowLeft, FaArrowRight } from 'react-icons/fa';
import ConfigModel from './components/treesequence.jsx'
import { observer } from 'mobx-react'

const Sidebar = observer(({ viewModel }) => {
  let nwk = viewModel.newick
  console.log("newick", nwk)
  const sourceData = {
    status: "loaded",
    filename: "test.nwk",
    data: nwk,
    filetype: "nwk",
    mutationtypeEnabled: true
  };

  return (
    <div className="h-[calc(100%-4rem)]">
      <TaxoniumBit sourceData={sourceData} />
    </div>
  );
});

function App() {

  // Import taxonium-component
  (() => {
    import("taxonium-component");
  }, []);
  
  const [dataState, setDataState] = useState('((A:0.1,B:0.2):0.3,(C:0.4,D:0.5):0.6);');
  const [inputValue, setInputValue] = useState('');

  const handleChange = (event) => {
    setInputValue(event.target.value);
  };

  const changenewick = (newick_string) => {
    setDataState(newick_string)
  };
      
  const json_data = {
    view: {
      newick: dataState
    }
  }
  const config = ConfigModel.create(json_data);

  useEffect(() => {

    config.view.update_newick(dataState)

  }, [dataState])

  return (
    <>
     <div>
      <div style={{ display: "flex", height: "100vh" }}>
        <div className="flex flex-col" style={{ width: '70%' }}>
          <Sidebar viewModel={config.view}/>
        </div>

        <div>
          <input type="text" value={inputValue} 
          placeholder="Enter newick string" 
          onChange={handleChange} 
          />
          <button onClick={() => changenewick(inputValue)}>
            Submit
          </button>
        </div>
      </div>
     </div>
    </>
);
}

export default App;
