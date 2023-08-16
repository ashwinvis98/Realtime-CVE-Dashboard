import React from "react";
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import { useState, useEffect } from 'react';
import axios from "axios";
  
function ThreatProliferation() {
  const [value, setValue] = React.useState('fruit');
  const optionsOne = [
    {label: 'All Time', value: 'all'},
    {label: 'Last Year', value: '1y'},
    {label: 'Last 3 Years', value: '3y'},
    {label: 'Last 5 Years', value: '5y'},
    {label: 'Last 10 Years', value: '10y'}
  ];

  const handleChange = (event) => {
    setValue(event.target.value);
  }

  const [options, setOptions] = useState({
    chart: {
      type: 'line'
    }, legend: {
      enabled: false
    },
    title: {
      text: ""
    },
    xAxis: {
      categories: [],
      title: {
        text: "Date"
      }
    },
    plotOptions: {
      series: {
        color: '#009bb0'
      }
    },
    yAxis: {
      title: {
        text: 'Vulnerability Count',
      },
      labels: {
        overflow: 'justify'
      },

    },
    series: [{data: []}]
  });



  useEffect(() => {
    let cancel = false;
    axios.get(window.host + "/api/v1.0/threat_proliferation", {params: {duration: value}}).then((response) => {
        if (cancel) return;
        let data = response.data;
        const xAxis=[];
        const yAxis=[];
        for (let i = 0; i < data.length; i++) {
          yAxis.push(data[i].count)
          xAxis.push(data[i].date)

        }
        setOptions({ xAxis: {
          categories: xAxis,
          title: {
              text: "Date"
          }
        }, series: [{ data: yAxis, name: "Vulnerability Count"}] });


      })

    return () => {
      cancel = true
    };
    
  },[value]);
  
  return (
    <div>
      <div className="d-flex justify-content-between">
        <h2 className="text-selected d-flex flex-column justify-content-end">Total Threats Over Time</h2>

        <select className="dropdown" value={value} onChange={handleChange}>
          {optionsOne.map((optionOne) => (
            <option value={optionOne.value}>{optionOne.label}</option>
          ))}
        </select>
      </div>

      <div className="content-box mt-2 pt-4">
        <HighchartsReact
          highcharts={Highcharts}
          options={options}
        />
      </div>
    </div>
  );
}
  
export default ThreatProliferation;
