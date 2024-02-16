// Create Data Source Page
import React, { useState, useEffect } from "react";
import Navbar from "../Navbar";
import axios from "axios";
import "./datasource.scss";

function Datasource() {
  const [datasource, setDatasource] = useState([]);
  const [error, setError] = useState(false);

  const fetchData = async () => {
    setError(false);
    try {
      const res = await axios.get("http://localhost:3000/datasource");
      setDatasource(res.data);
    } catch (err) {
      setError(true);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="header">
      <Navbar />
          
    </div>
  );
}

export default Datasource;
