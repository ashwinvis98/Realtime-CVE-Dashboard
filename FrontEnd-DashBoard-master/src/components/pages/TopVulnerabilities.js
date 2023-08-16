import React from "react";
import {useState, useEffect} from 'react';
import {ScoreCircle, LoadingSpinner} from '../Components'
import axios from "axios";

function TopVulnerabilities() {
  const [value, setValue] = React.useState('all');
  const [loading, setLoading] = useState(true);
  const optionsOne = [
    {label: 'All Time', value: 'all'},
    {label: 'Last 24 Hours', value: '1d'},
    {label: 'Last 4 Days', value: '4d'},
    {label: 'Last Week', value: '1w'},
    {label: 'Last Month', value: '1m'},
    {label: 'Last 3 Months', value: '3m'},
    {label: 'Last 6 Months', value: '6m'},
    {label: 'Last Year', value: '1y'},
    {label: 'Last 3 Years', value: '3y'},
    {label: 'Last 5 Years', value: '5y'},
    {label: 'Last 10 Years', value: '10y'}
  ];

  const [topVulnerabilities, setTopVulnerabilities] = useState([{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]);

  const handleChange = (event) => {
    setValue(event.target.value);
  };

  useEffect(() => {
    let cancel = false;
    axios.get(window.host + "/api/v1.0/top_cves", {params: {duration: value}}).then((response) => {
      let data = response.data;
      if (cancel) return;
      setTopVulnerabilities(data)
      setLoading(false)
    })

    return () => {
      cancel = true;
    }

  }, [value]);
  return (
    <div>
      <div className="d-flex justify-content-between">
        <h2 className="text-selected d-flex flex-column justify-content-end">Top Vulnerabilities</h2>

        <select className="dropdown" value={value} onChange={handleChange}>
          {optionsOne.map((optionOne) => (
            <option value={optionOne.value}>{optionOne.label}</option>
          ))}
        </select>
      </div>

      <div className="content-box mt-2 pt-3 ps-4 pe-4 pb-3" style={{maxHeight: "70vh", overflowY: "scroll"}}>
        {loading ? <LoadingSpinner/> : (
          <>
            {topVulnerabilities.map((topVulnerability) => {
              let index = topVulnerabilities.indexOf(topVulnerability);
              let url = topVulnerability.cve_id ? "https://nvd.nist.gov/vuln/detail/" + topVulnerability.cve_id : "";
              return (
                <div className="d-flex justify-content-start mt-3">
                  <ScoreCircle className="flex-shrink-0">{index+1}</ScoreCircle>
                  <div className="ms-3">
                    <h5><a href={url} target="_blank" className="text-selected">{topVulnerability.cve_id}</a>{topVulnerability.cvss && <span className="ms-3 text-muted small">CVS Score: {topVulnerability.cvss}</span>}</h5>
                    <div>{topVulnerability.summary}</div>
                  </div>
                </div>
              )
            })}
          </>
        )}
      </div>
    </div>
  );
}

export default TopVulnerabilities;
