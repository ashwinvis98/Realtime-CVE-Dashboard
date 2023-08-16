import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import "./styles.css";
import { Routes ,Route, BrowserRouter } from 'react-router-dom';
import TopVulnerabilities from './components/pages/TopVulnerabilities'
import ThreatProliferation from './components/pages/ThreatProliferation';
import ImpactOverTheYears from './components/pages/ImpactOverTheYears';
import ThreatsChangedOverTime from './components/pages/ThreatsChangedOverTime';
import Clustering from './components/pages/Clustering';
import VendorsSection from './components/pages/VendorsSection';
import ProductsSection from './components/pages/ProductsSection';
import Dashboard from './components/Dashboard';
import 'bootstrap/dist/css/bootstrap.min.css';

if(process.env.NODE_ENV === 'development')
  window.host = "http://localhost:5000";
else
  window.host = "";

document.title = "CVE Live Dashboard";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path='/dashboard' element={<Dashboard/>} />
        <Route path='/TopVulnerabilities' element={<TopVulnerabilities/>} />
        <Route path='/ThreatProliferation' element={<ThreatProliferation/>} />
        <Route path='/ImpactOverTheYears' element={<ImpactOverTheYears/>} />
        <Route path='/ThreatsChangedOverTime' element={<ThreatsChangedOverTime/>} />
        <Route path='/Clustering' element={<Clustering/>} />
        <Route path='/VendorsSection' element={<VendorsSection/>} />
        <Route path='/ProductsSection' element={<ProductsSection/>} />
        <Route path='/' element={<App/>} />
      </Routes>
    </BrowserRouter>
   
  </React.StrictMode>
);
