import React, { useState, useEffect, useRef } from 'react';
import Plotly from 'plotly.js/dist/plotly-cartesian';
import createPlotlyComponent from 'react-plotlyjs';
import './Graphs.css';

const PlotlyComponent = createPlotlyComponent(Plotly);

const Graphs = () => {
    const [plots, setPlots] = useState([]);
    //748cab
    const plot_bg_colour = "#748cab";
    const [plotSize, setPlotSize] = useState({});
    const plotSizeRef = useRef({});
    const currentId = useRef(-1);

    const arrayChunk = (arr, n) => {
      const array = arr.slice();
      const chunks = [];
      while (array.length) chunks.push(array.splice(0, n));
      return chunks;
    };
    
    useEffect(() => {
      fetch('http://127.0.0.1:5000/graphs', 
      {
        method: 'GET', 
        mode: 'cors',
      }).then(
        res => {
        // res.set({
        //     "Content-Type": "application/json",
        //     "Access-Control-Allow-Origin": "*",
        // });
        return res.json()}
      ).then(
        data => 
        {
            var plotSizes = {};
            data = data.map((d, idx) => {
              var d_json = JSON.parse(d);
              plotSizes = {...plotSizes, [idx]: ['350px','200px', 6, 12]}
              return d_json;
            })
            setPlotSize(plotSizes);
            console.log(data);
            console.log(plotSizes);
            plotSizeRef.current = plotSizes;
            console.log(plotSize);
            setPlots(data);
        });
      }, []);
      // console.log(plot)
    
    return (
     
      <div className='content'>
   

       {arrayChunk(plots, 3).map((row, i) => (
        <div key={i} className="graph-row">
          {row.map((d, idx) => {
            return ( <div className='graphContainer' style={{width: plotSize[i * 3 + idx][0], height: plotSize[i * 3 + idx][0]}}  onMouseEnter={() => {
              if(currentId.current !== i * 3 + idx){
              console.log("GRAPH");
              setPlotSize({...plotSizeRef.current, [i*3 + idx]: ['550px', '300px', 10, 16]}); 
              currentId.current = i * 3 + idx;}
            }} 
            // onMouseLeave={(e) => {
            //   console.log("BG");
            //   console.log(document.elementFromPoint(e.clientX, e.clientY))
            //   setPlotSize(plotSizeRef.current); currentId.current = -1;
            //   console.log(e);
            //   }}
              >
            <PlotlyComponent data={d.data} layout={{...d.layout, paper_bgcolor: plot_bg_colour, plot_bgcolor: plot_bg_colour, font:{size:plotSize[i * 3 + idx][2]}, title:{text: d.layout.title.text, font:{size:plotSize[i * 3 + idx][3]}}}} className="Graph" key={i*3 + idx}></PlotlyComponent>
            {/* <div className='graphTitle'>{d.layout.title.text}</div> */}
            </div>)
        })}
        </div>
      ))}

     

      </div>
    );
};

export default Graphs;