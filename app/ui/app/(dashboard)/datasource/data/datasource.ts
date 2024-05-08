export const types = ["Data Warehouse", "Database"] as const

export type DataSourceType = (typeof types)[number]

export interface DataSource {
  id: number;
  name: string;
  label: string;
  description: string;
  type?: string;
  icon?: string;
  status: string;
  tags?: string[];
}

export const dataSources: DataSource[] = [
  {
    id: 1,
    name: "Snowflake",
    type: "Data Warehouse",
    description: "Snowflake data warehouse",
    status: "disconnected",
    label: "snowflake",
  },
  {
    id: 2,
    name: "PostgreSQL",
    type: "Database",
    description: "PostgreSQL database",
    status: "disconnected",
    label: "postgresql",
  },
  {
    id: 3,
    name: "BigQuery",
    type: "Data Warehouse",
    description: "BigQuery data warehouse",
    status: "disconnected",
    label: "bigquery",
  },
  {
    id: 4,
    name: "Redshift",
    type: "Data Warehouse",
    description: "Redshift data warehouse",
    status: "disconnected",
    label: "redshift",
  },
  {
    id: 5,
    name: "MongoDB",
    type: "Database",
    description: "MongoDB database",
    status: "disconnected",
    label: "mongodb",
  },
];