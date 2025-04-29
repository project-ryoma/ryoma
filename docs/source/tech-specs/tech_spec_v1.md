
# Ryoma tech spec v1

This document describes the technical specifications of the project.

## Overview

### V1 Architecture

![Architecture](Architecture_v1.png)

## Components

Each design component map to an interface, as well as a database table.

### A) Data Sources
A data source contains the connector to the underlying db

#### UI

#### API


#### Service


### B) Catalogs
Data Catalogs contain the information (description/schema/data types) of data sources. Specifically, the catalogs include:

1. Name
Name of the data source.
2. Type
Database, Schema, or Table.
3. Description
4. Schema
Schema of the table.
5. Data Types
Each type of the column in the table.
6. Metadata
Size of the data source.

### C) Vector store
Vector store is used for storing the indexes of the data catalogs, as well as the user custom RAG content.

#### APIs