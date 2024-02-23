"use client";
import { Card } from "@/components/ui/card";
import { DataSourceModal } from "./data-source-modal";
import {DataSource} from "./data/datasource";
import { useState } from "react";
import axios from "axios";
import * as z from "zod";
import cn from "classnames";

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
    
    try {
      // if successful, update the status of the data source
      // and close the modal
      const response = await axios.post("/api/datasource/connect", {
        datasource: dataSource.label,
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
      <Card
        className="hover:bg-accent hover:text-accent-foreground hover:cursor-pointer"
        onClick={() => setModalOpen(true)}>
        <div className="space-y-2 p-4">
          <h3 className="flex items-center justify-between">
            {dataSource.name}
            <span
              className={cn("text-xs rounded-full px-1 py-1", {
                "bg-green-500 text-white": dataSource.status === "connected",
                "bg-red-500 text-white": dataSource.status === "disconnected",
              })}
            />
          </h3>
          <p className="text-gray-500">{dataSource.type}</p>
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