// create a data source page to display the data sources
// data source page should contain a data source board to display the data sources

import DataSourceBoard from "./data-source-board";
import BreadCrumb from "@/components/breadcrumb";
import { Heading } from "@/components/ui/heading";
import React from "react";

const breadcrumbItems = [{ title: "Data Source", link: "/dashboard/datasource" }];
export default function page() {
  return (
    <>
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <BreadCrumb items={breadcrumbItems} />
        <div className="flex items-start justify-between">
          <Heading title={`Data Source`} description="Manage your Data Source" />
        </div>
        <DataSourceBoard />
      </div>
    </>
  );
}