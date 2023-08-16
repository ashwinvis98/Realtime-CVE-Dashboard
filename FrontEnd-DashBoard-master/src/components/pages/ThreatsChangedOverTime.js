import React, {useEffect, useState} from "react";
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
  
function ThreatsChangedOverTime() {let [value, setValue] = React.useState('one');
  const optionsOne = [
    {label: 'All Time', value: 'all'},
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
        text: 'Count',
      },
      max: 300,
      labels: {
        overflow: 'justify'
      },

    },
    series: [{data: []}]
  });


  const [xAxisData, setxAxisData] = useState(null)
  const [yAxisData, setyAxisData] = useState(null)

  useEffect(() => {
    fetch(window.host + "/api/v1.0/vulnerability_type")
     .then((response) => response.json())
     .then((data) => {
      const xAxis=[];
      const yAxes={};
      for (let i = 0; i < data.length; i++) {
        // for every attribute in data[i], add it to the yAxes object (except for date, which is the x-axis)
        // yAxis.push(data[i].count)
        // xAxis.push(data[i].date)
        for (const [key, value] of Object.entries(data[i])) {
          if (key !== "date") {
            if (yAxes[key] === undefined) {
              yAxes[key] = [];
            }
            yAxes[key].push(value);
          } else {
            xAxis.push(value);
          }
        }
    }

    let series = []
    let colors = ['#009bb0', '#ff6c00', '#ff0000', '#00ff00', '#0000ff', '#ff00ff', '#cc6666', '#00ffff', '#000000', '#ffffff']
    for (const [key, value] of Object.entries(yAxes)) {
      series.push({name: key, data: value, color: colors.pop()})
    }
    // setxAxisData(xAxis);
    // setyAxisData(yAxis);
    setOptions({ xAxis: {
      categories: xAxis,
      title: {
          text: "Date"
      }
  }, series: series });


    })

  },[]);

  return (
    <div>
      <div className="d-flex justify-content-between">
        <h2 className="text-selected d-flex flex-column justify-content-end">How Threats Have Changed Over Time</h2>

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
  
export default ThreatsChangedOverTime;
