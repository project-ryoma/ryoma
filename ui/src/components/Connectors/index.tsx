import React, { useEffect, useState } from "react";
import Navbar from "../Navbar";
import { Link } from "react-router-dom";
import axios from "axios";
import "./connectors.css";

function createData(
  id: number,
  connector_name: string,
  connector_status: string,
  connector_type: string
) {
  return { id, connector_name, connector_status, connector_type };
}

const connectors = [
  { id: 1, name: "MySQL", status: "Active", type: "Database" },
  { id: 2, name: "Snowflake", status: "Active", type: "Database" },
  // ... other connectors
];

function Connectors() {

  return (
    <div className="header">
      <div className="header__content">
        <Navbar />
        <div className="connectors">
          {connectors.map((connector) => (
            <div key={connector.id} className="connector">
              <Link to={`/authenticate/${connector.name}`}>
                <button className="connector-button">
                  {connector.name}
                </button>
              </Link>
              <p>Status: {connector.status}</p>
              <p>Type: {connector.type}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Connectors;