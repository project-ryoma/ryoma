// create a data source page to display the data sources
// data source page should contain a data source board to display the data sources

import React from "react";
import BreadCrumb from "@/components/breadcrumb";
import { DataSourceClient } from "@/app/(dashboard)/datasource/components/data-source-client";
import { dataSources } from "./data/datasource"; 

const breadcrumbItems = [{ title: "Data Source", link: "/dashboard/datasource" }];
export default function page() {
  return (
    <>
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <BreadCrumb items={breadcrumbItems} />
        <DataSourceClient data={dataSources} />
      </div>
    </>
  );
}