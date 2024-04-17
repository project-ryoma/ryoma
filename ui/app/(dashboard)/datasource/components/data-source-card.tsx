"use client";
import { Card } from "@/components/ui/card";
import {DataSource} from "../data/datasource";
import cn from "classnames";

type DataSourceCardProps = {
  dataSource: DataSource;
  onClick: () => void;
};

export function DataSourceCard({ dataSource, onClick }: DataSourceCardProps) {
  return (
      <Card
        className="hover:bg-accent hover:text-accent-foreground hover:cursor-pointer"
        >
        <div className="space-y-2 p-4">
          <h3 className="items-center justify-between">
            {dataSource.name}
          </h3>
          <p className="text-gray-500">{dataSource.type}</p>
        </div>
      </Card>
  );
}