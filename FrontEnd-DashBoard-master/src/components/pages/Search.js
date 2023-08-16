import React, {useEffect, useState} from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import {Nav, NavTitle} from '../NavbarElements';
import {LoadingSpinner} from "../Components";
import axios from "axios";
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import {XLg, PlusLg} from "react-bootstrap-icons";

const COLORS = [
  "hsl(0, 100%, 40%)",
  "hsl(30, 100%, 40%)",
  "hsl(60, 100%, 40%)",
  "hsl(90, 100%, 40%)",
  "hsl(120, 100%, 40%)",
  "hsl(150, 100%, 40%)",
  "hsl(180, 100%, 40%)",
  "hsl(210, 100%, 40%)",
  "hsl(240, 100%, 40%)",
  "hsl(270, 100%, 40%)",
  "hsl(300, 100%, 40%)",
  "hsl(330, 100%, 40%)"
]

function getColors(numColors) {
  let colors = [];
  for (let i = 0; i < numColors; i++) {
    colors.push(COLORS[i % COLORS.length]);
  }
  return colors;
}

const COLLECTION_TYPE_INFO = {
  "vendors": {
    text: "Vendors",
    get_items_url: "/api/v1.0/get_vendors",
    get_data_url: "/api/v1.0/vendor_history",
  },
  "products": {
    text: "Products",
    get_items_url: "/api/v1.0/get_products",
    get_data_url: "/api/v1.0/product_history",
  },
  "cwes": {
    text: "Vulnerability Types",
    get_items_url: "/api/v1.0/vulnerability_types",
    get_data_url: "/api/v1.0/vulnerability_type_history",
  }
}

function Search(props) {
  // const text = props.is_vendors ? "Vendors" : "Products";
  // const get_items_url = props.is_vendors ? "/api/v1.0/get_vendors" : "/api/v1.0/get_products";
  // const get_data_url = props.is_vendors ? "/api/v1.0/vendor_history" : "/api/v1.0/product_history";
  const text = COLLECTION_TYPE_INFO[props.collection_type].text;
  const get_items_url = COLLECTION_TYPE_INFO[props.collection_type].get_items_url;
  const get_data_url = COLLECTION_TYPE_INFO[props.collection_type].get_data_url;

  const [search, setSearch] = useState("");
  const [items, setItems] = useState([]);
  const [availableItems, setAvailableItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [loading, setLoading] = useState(true);

  let [value, setValue] = useState('one');
  const optionsOne = [
    {label: 'All Time', value: 'all'},
  ];

  const handleChange = (event) => {
    setValue(event.target.value);
  }

  const handleSearch = (event) => {
    setSearch(event.target.value);
  }

  useEffect(() => {
    if (search.length > 0) {
      let items = searchItems(search);
      setItems(items);
    }
  }, [search, selectedItems]);

  const searchItems = (val) => {
    let words = val.split(" ");
    let rankedItems = [];
    availableItems.forEach((item) => {
      if (!item_is_selected(item)) {
        let rank = 0;
        let item_name = item.toLowerCase();
        let ranked = false;
        words.forEach((word) => {
          let index = item_name.indexOf(word.toLowerCase());
          if (index > -1 && word !== "") {
            rank += 20 - index + word.length;
            ranked = true;
          }
        });
        if (ranked) {
          rankedItems.push({item: item, rank: rank});
        }
      }
    });
    rankedItems.sort((a, b) => {
      if (a.rank === b.rank) {
        // sort alphabetically by item.item
        return a.item.localeCompare(b.item);
      }
      return b.rank - a.rank;
    });
    return rankedItems.slice(0, 100).map((item) => {
      return {item: item.item, label: prettify(item.item)};
    });
  }

  const item_is_selected = (item) => {
    for (let i = 0; i < selectedItems.length; i++) {
      if (selectedItems[i].item === item) {
        return true;
      }
    }
    return false;
  }

  const prettify = (item) => {
    item = item.replace(/\\/g, "");
    let words = item.split("_");
    let prettified = "";
    words.forEach((word) => {
      prettified += word.charAt(0).toUpperCase() + word.slice(1) + " ";
    });
    return prettified;
  }

  const get_highlighted_item = (item, search) => {
    // return the item, but with the search terms bolded
    let words = search.split(" ");
    let highlighted = item;
    words.forEach((word) => {
      let index = highlighted.toLowerCase().indexOf(word.toLowerCase());
      if (index > -1 && word !== "") {
        highlighted = highlighted.substring(0, index) + "<b>" + highlighted.substring(index, index + word.length) + "</b>" + highlighted.substring(index + word.length);
      }
    });
    return <span dangerouslySetInnerHTML={{__html: highlighted}}/>;
  }

  const select_item = (item) => {
    setSelectedItems(prevState => [...prevState, item]);
  }

  const deselect_item = (item) => {
    setSelectedItems(prevState => prevState.filter((i) => i !== item));
  }

  const reset_search_input = () => {
    setSearch("");
    document.getElementById("searchInput").value = "";
  }

  useEffect(() => {
    let t = setTimeout(() => {
      axios.get(window.host + get_items_url).then((response) => {
        if (response.status === 200) {
          setAvailableItems(response.data.items);
          if (response.data.top_items) {
            setSelectedItems(response.data.top_items.map((item) => {
              return {item: item, label: prettify(item)};
            }));
          }
          setLoading(false);
        }
      });
    }, 100);
    return () => clearTimeout(t);
  }, []);

  const [options, setOptions] = useState({
    chart: {
      type: 'line'
    }, legend: {
      enabled: false
    },
    title: {
      text: `Vulnerability Count Over Time by ${text}`
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
      labels: {
        overflow: 'justify'
      },

    },
    series: [{data: []}]
  });

  useEffect(() => {
    let cancel = false;

    axios.get(window.host + get_data_url, {params: {items: selectedItems.map(item => item.item).join(",")}}).then((response) => {
      if (response.status === 200 && !cancel) {
        let xAxis = [];
        let series = {};
        for (let i= 0; i < response.data.length; i++) {
          for (const [key, value] of Object.entries(response.data[i])) {
            if (key !== "date") {
              if (series[key] === undefined) {
                series[key] = [];
              }
              series[key].push(value);
            } else {
              xAxis.push(value);
            }
          }
        }

        let clean_series = [];
        let colors = getColors(series.length)
        for (const [key, value] of Object.entries(series)) {
          let color = colors.pop();
          clean_series.push({name: prettify(key), data: value, color: color});
        }

        setOptions({
          xAxis: {
            categories: xAxis,
            title: {
              text: "Date"
            }
          },
          series: clean_series,
          title: {
            text: `Vulnerability Count Over Time by ${text}`
          },
          yAxis: {
            title: {
              text: 'Vulnerability Count',
            }
          }
        });
      }
    });

    return () => {
      cancel = true
    };
  }, [selectedItems]);

  return (
    <>
      {loading ? <LoadingSpinner/> : (
        <div>
          <div className="d-flex justify-content-between">
            <h2 className="text-selected d-flex flex-column justify-content-end">Search {text}</h2>

            {/*<select className="dropdown" value={value} onChange={handleChange}>*/}
            {/*  {optionsOne.map((optionOne) => (*/}
            {/*    <option value={optionOne.value}>{optionOne.label}</option>*/}
            {/*  ))}*/}
            {/*</select>*/}
          </div>

          <Row>
            <Col xs={4}>
              <input id="searchInput" className="search-input mt-2" placeholder="Search" onChange={handleSearch}></input>
              {search && (
                <>
                  <Button variant="outline-secondary" className="w-100 mt-1" onClick={reset_search_input}>Clear</Button>
                  <div className="content-box search-results mt-2">
                    {items.map((item) => (
                      <div className="search-result d-flex justify-content-between" onClick={() => select_item(item)}>
                        <div>{get_highlighted_item(item.label, search)}</div><PlusLg className="text-success me-1 text-lg"></PlusLg>
                      </div>
                    ))}
                  </div>
                </>
              )}
              <Nav className="mt-2 pb-2">
                <NavTitle>Selected {text}</NavTitle>
                {selectedItems.length === 0 ? (
                  <div className="text-center mt-2 text-muted">No items selected</div>
                  ) : (
                  <div className="mt-2">
                    {selectedItems.map((item) => (
                      <div className="search-result d-flex justify-content-between" onClick={() => deselect_item(item)}>
                        <div>{item.label}</div><XLg className="text-danger me-1 text-lg"></XLg>
                      </div>
                    ))}
                  </div>
                  )
                }
              </Nav>
            </Col>
            <Col xs={8}>
              <div className="content-box mt-2 pt-4">
                <HighchartsReact
                  highcharts={Highcharts}
                  options={options}
                />
              </div>
            </Col>
          </Row>
        </div>
      )}
    </>
  );
}

export default Search;
