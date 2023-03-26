import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js/dist/plotly-cartesian';
import createPlotlyComponent from 'react-plotlyjs';
import './Graphs.css';

const PlotlyComponent = createPlotlyComponent(Plotly);

const Graphs = () => {
    const [plots, setPlots] = useState([]);
    //748cab
    const plot_bg_colour = "#F5F3ED";
    
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
            data = data.map((d, idx) => {
              var d_json = JSON.parse(d);
             
              return d_json;
            })
            console.log(data);
            setPlots(data);
        });
    }, []);
      // console.log(plot)
    
    return (
      <div className='content'>
      {plots.map(function(d, idx){
         return ( <div className='graphContainer'>
          <PlotlyComponent data={d.data} layout={{...d.layout, width: 1000, height: 550, paper_bgcolor: plot_bg_colour, plot_bgcolor: plot_bg_colour}} className="Graph" key={idx}></PlotlyComponent>
          {/* <div className='graphTitle'>{d.layout.title.text}</div> */}
          </div>)
       })}

     

      </div>
    );
};

export default Graphs;