
export interface DataSource {
  id: string;
  name: string;
  label: string;
  description?: string;
  type?: string;
  icon?: string;
  status: string;
  tags?: string[];
}

export const dataSources: DataSource[] = [
  {
    id: "1",
    name: "Snowflake",
    type: "Data Warehouse",
    status: "disconnected",
    label: "snowflake",
  },
  {
    id: "2",
    name: "PostgreSQL",
    type: "Database",
    status: "disconnected",
    label: "postgresql",
  },
  {
    id: "3",
    name: "BigQuery",
    type: "Data Warehouse",
    status: "disconnected",
    label: "bigquery",
  },
  {
    id: "4",
    name: "Redshift",
    type: "Data Warehouse",
    status: "disconnected",
    label: "redshift",
  },
  {
    id: "5",
    name: "MongoDB",
    type: "Database",
    status: "disconnected",
    label: "mongodb",
  },
  {
    id: "6",
    name: "MySQL",
    type: "Database",
    status: "disconnected",
    label: "mysql",
  },
  {
    id: "7",
    name: "Elasticsearch",
    type: "Search Engine",
    status: "disconnected",
    label: "elasticsearch",
  },
  {
    id: "8",
    name: "Cassandra",
    type: "Database",
    status: "disconnected",
    label: "cassandra",
  },
  {
    id: "9",
    name: "Couchbase",
    type: "Database",
    status: "disconnected",
    label: "couchbase",
  },
  {
    id: "10",
    name: "DynamoDB",
    type: "Database",
    status: "disconnected",
    label: "dynamodb",
  },
  {
    id: "11",
    name: "Hive",
    type: "Data Warehouse",
    status: "disconnected",
    label: "hive",
  },
  {
    id: "12",
    name: "Impala",
    type: "Data Warehouse",
    status: "disconnected",
    label: "impala",
  },
  {
    id: "13",
    name: "MemSQL",
    type: "Database",
    status: "disconnected",
    label: "memsql",
  },
  {
    id: "14",
    name: "Presto",
    type: "Data Warehouse",
    status: "disconnected",
    label: "presto",
  },
  {
    id: "15",
    name: "Pulsar",
    type: "Database",
    status: "disconnected",
    label: "pulsar",
  },
  {
    id: "16",
    name: "Redis",
    type: "Database",
    status: "disconnected",
    label: "redis",
  },
];