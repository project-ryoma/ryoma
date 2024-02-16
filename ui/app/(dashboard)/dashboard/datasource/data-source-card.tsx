"use client";
import { DataSource } from "@/types/index";
import { Card } from "@/components/ui/card";
import { DataSourceStatus } from "./data-source-status";
import { DataSourceModal } from "./data-source-modal";
import { useState } from "react";
import axios from "axios";
import * as z from "zod";

type DataSourceCardProps = {
  dataSource: DataSource;
  onClick: () => void;
};

const formSchema = z.object({
  user: z.string(),
  password: z.string(),
  host: z.string(),
  port: z.number(),
  database: z.string(),
  schema: z.string(),
  type: z.string(),
  role: z.string(),
});


export function DataSourceCard({ dataSource, onClick }: DataSourceCardProps) {
  const [modalOpen, setModalOpen] = useState(false);

  const handleSubmit = async (values: z.infer<typeof formSchema>) => {
    // call api to connect to the data source
    
    console.log("values", values)
    try {
      // if successful, update the status of the data source
      // and close the modal
      const response = await axios.post(`/api/py/connect-datasource?datasource=${dataSource.label}`, {
        ...values,
      });

      // update the status of the data source based on the response
      
      if (response.data.status === 200) {
        dataSource.status = "connected";
      } else {
        dataSource.status = "disconnected";
      }

    } catch (error) {
      // if failed, show an error message
    }

    // close the modal
    setModalOpen(false);
  }

  return (
    <>
      <Card onClick={() => setModalOpen(true)}>
        <div className="space-y-2 p-4">
          <h3 className="text-lg font-semibold">{dataSource.name}</h3>
          <DataSourceStatus status={dataSource.status} />
          <p className="text-sm text-gray-500">{dataSource.type}</p>
        </div>
      </Card>
      <DataSourceModal
        dataSource={dataSource}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
      />
    </>
  );
}