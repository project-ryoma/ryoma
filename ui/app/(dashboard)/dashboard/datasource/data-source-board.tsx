"use client";
import { DataSourceCard } from "./data-source-card";
import { useState } from "react";
import { dataSources } from "./data/datasource";


const DataSourceBoard = () => {
  const [searchValue, setSearchValue] = useState("");

  return (
    <div className="p-4 space-y-4">
      <input
        type="text"
        placeholder="Search data source..."
        value={searchValue}
        onChange={(e) => setSearchValue(e.target.value)}
        className="w-full p-2 border rounded-lg"
      />
      <div className="grid grid-cols-3 gap-4">
        {dataSources
          .filter((dataSource) =>
            dataSource.name.toLowerCase().includes(searchValue.toLowerCase())
          )
          .map((dataSource) => (
            <DataSourceCard
              key={dataSource.id}
              dataSource={dataSource}
              onClick={() => {}}
            />
          ))}
      </div>
    </div>
  );
}

export default DataSourceBoard;