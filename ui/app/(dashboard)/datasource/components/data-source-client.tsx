"use client";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { Heading } from "@/components/ui/heading";
import { Separator } from "@/components/ui/separator";
import { DataSource } from "../data/datasource";
import { Plus } from "lucide-react";
import { useState } from "react";
import { columns } from "./columns";
import { DataSourceModal } from "./data-source-modal";

interface ProductsClientProps {
  data: DataSource[];
}

export const DataSourceClient: React.FC<ProductsClientProps> = ({ data }) => {
  const [modelOpen, setModelOpen] = useState(false);

  return (
    <>
      <div className="flex items-start justify-between">
        <Heading
          title={`Data Sources (${data.length})`}
          description="Manage data sources."
        />
        <Button
          className="text-xs md:text-sm"
          onClick={() => setModelOpen(true)}
        >
          <Plus className="mr-2 h-4 w-4" /> Add New
        </Button>
      </div>
      <Separator />
      <DataTable searchKey="name" columns={columns} data={data} />
      <DataSourceModal
        dataSources={data}
        isOpen={modelOpen}
        onClose={() => setModelOpen(false)}
      />
    </>
  );
};
