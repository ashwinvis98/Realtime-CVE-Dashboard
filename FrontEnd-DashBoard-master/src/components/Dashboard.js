import React from "react";
import TitleBar from "./TitleBar";
import {useState, useEffect} from 'react';
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";
import Container from "react-bootstrap/Container";
import {Nav, NavTitle, NavLink, SubscriptionNav, SubscriptionButton} from './NavbarElements';
import axios from "axios";
import {useNavigate} from "react-router-dom";
import TopVulnerabilities from "./pages/TopVulnerabilities";
import ThreatProliferation from "./pages/ThreatProliferation";
import ImpactOverTheYears from "./pages/ImpactOverTheYears";
import Clustering from "./pages/Clustering";
import VendorsSection from "./pages/VendorsSection";
import ProductsSection from "./pages/ProductsSection";
import Search from "./pages/Search";

function Dashboard() {
  const [activePage, setActivePage] = useState("ThreatProliferation");
  const [accountInfo, setAccountInfo] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    axios.post(window.host + "/api/v1.0/user_session", {
      "user_id": localStorage.getItem("user_id")
    }).then((response) => {
      if (response.status === 200) {
        setAccountInfo(response.data.user);
      } else {
        localStorage.removeItem("user_id");
        navigate("/");
      }
    });
  }, []);

  function signOut() {
    localStorage.removeItem("user_id");
    navigate("/");
  }

  function setSubscription(subscribe) {
    axios.post(window.host + "/api/v1.0/set_subscription", {
      "user_id": localStorage.getItem("user_id"),
      "subscribe": subscribe
    }).then((response) => {
      if (response.status === 200) {
        setAccountInfo(response.data.user);
      } else {
        localStorage.removeItem("user_id");
        navigate("/");
      }
    });
  }

  return (
    <main>
      <TitleBar/>
      <Container className="main-window pt-5 pb-5">
        <Row>
          <Col xs={9}>
            {activePage === "TopVulnerabilities" && <TopVulnerabilities/>}
            {activePage === "ThreatProliferation" && <ThreatProliferation/>}
            {activePage === "ImpactOverTheYears" && <ImpactOverTheYears/>}
            {activePage === "ThreatsChangedOverTime" && <Search collection_type={"cwes"}/>}
            {activePage === "Clustering" && <Clustering/>}
            {activePage === "VendorsSection" && <VendorsSection/>}
            {activePage === "ProductsSection" && <ProductsSection/>}
            {activePage === "SearchVendors" && <Search collection_type={"vendors"}/>}
            {activePage === "SearchProducts" && <Search collection_type={"products"}/>}
          </Col>
          <Col xs={3}>
            <Nav>
              <NavTitle>Pages</NavTitle>
              <NavLink onClick={() => setActivePage("ThreatProliferation")} activeStyle className={activePage === "ThreatProliferation" ? "text-selected" : ""}>Total Threats Over Time</NavLink>
              <NavLink onClick={() => setActivePage("SearchVendors")} activeStyle className={activePage === "SearchVendors" ? "text-selected" : ""}>Search Vendors</NavLink>
              <NavLink onClick={() => setActivePage("SearchProducts")} activeStyle className={activePage === "SearchProducts" ? "text-selected" : ""}>Search Products</NavLink>
              <NavLink onClick={() => setActivePage("ThreatsChangedOverTime")} activeStyle className={activePage === "ThreatsChangedOverTime" ? "text-selected" : ""}>Search Vulnerability Types</NavLink>
              <NavLink onClick={() => setActivePage("VendorsSection")} activeStyle className={activePage === "VendorsSection" ? "text-selected" : ""}>Top Vendors</NavLink>
              <NavLink onClick={() => setActivePage("ProductsSection")} activeStyle className={activePage === "ProductsSection" ? "text-selected" : ""}>Top Products</NavLink>
              <NavLink onClick={() => setActivePage("TopVulnerabilities")} activeStyle className={activePage === "TopVulnerabilities" ? "text-selected" : ""}>Top Vulnerabilities</NavLink>
              {/*<NavLink onClick={() => setActivePage("Clustering")} activeStyle className={activePage === "Clustering" ? "text-selected" : ""}>Clustering</NavLink>*/}
              {/*<NavLink onClick={() => setActivePage("ImpactOverTheYears")} activeStyle className={activePage === "ImpactOverTheYears" ? "text-selected border-bottom-0" : "border-bottom-0"}>Impact Over The Years</NavLink>*/}
            </Nav>
            <Nav className="mt-3 p-2 ps-3 pe-3">
              <NavTitle>Account</NavTitle>
              <h5 className="mb-0 mt-2"><b>{accountInfo.name}</b></h5>
              <div>{accountInfo.email}</div>
              <NavLink onClick={signOut} activeStyle className="border-bottom-0 text-end">Sign Out</NavLink>
            </Nav>
            {accountInfo.subscribed ? (
                <Nav className="mt-3 text-center">
                  <NavTitle>Subscription</NavTitle>
                  <div className="mt-3 text-center">You are subscribed to our email list.</div>
                  <SubscriptionButton className="mt-2 mb-2" onClick={() => setSubscription(false)}>Unsubscribe</SubscriptionButton>
                </Nav>
              ) : (
                <SubscriptionNav className="mt-3 text-center">
                  <h5><b>Subscription</b></h5>
                  <div>Subscribe to our email list to get notified of new vulnerabilities as they are discovered.</div>
                  <SubscriptionButton className="mt-2 mb-2" onClick={() => setSubscription(true)}>Subscribe</SubscriptionButton>
                </SubscriptionNav>
              )}
          </Col>
        </Row>
      </Container>
    </main>
  );
}

export default Dashboard;
