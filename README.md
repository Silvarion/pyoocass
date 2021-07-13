# pyoocass

Python Obect Oriented approach to Cassandra compliant document stores

## Classes

### **Database**
This class represents the Database object, meaning a cluster or serverles service from a cloud provider.

#### Attributes
| Attribute Name | Type  | Default Value | Description                                                                              |
|----------------|-------|---------------|------------------------------------------------------------------------------------------|
| nodes          | list  | _empty list_  | List of nodes/endpoints to connect to                                                    |
| port           | int   | 9042          | Port to connect to Cassandra/Keyspaces                                                   |
| user           | str   | ""            | Username to connect (can be ommited if auth_provider is provided in the Constructor)     |
| password       | str   | ""            | Password to connect (can be ommited if auth_provider is provided in the Constructor)     |
| cert           | str   | None          | Path to certificate if SSL is required                                                   |
| auth_provider  | Class | None          | An instance of any cassandra.auth classes or SigV4AuthProvider from cassandra_sigv4.auth |
| retries        | int   | 5             | Internal retries value for improved                                                      |
 
#### Methods
`__init__`

| Parameter name | Type  | Required | Default Value | Description                                                                              |
|----------------|-------|----------|---------------|------------------------------------------------------------------------------------------|
| nodes          | list  | Yes      | None          | List of cassandra cluster nodes/endpoints                                                |
| port           | int   | No       | 9042          | Port to connect to Cassandra/Keyspaces                                                   |
| user           | str   | No       | None          | Username to connect (can be ommited if auth_provider is provided in the Constructor)     |
| password       | str   | No       | None          | Password to connect (can be ommited if auth_provider is provided in the Constructor)     |
| cert           | str   | No       | None          | Path to certificate if SSL is required                                                   |
| auth_provider  | Class | No       | None          | An instance of any cassandra.auth classes or SigV4AuthProvider from cassandra_sigv4.auth |

`connect`

### **Keysapce**
**_NOT IMPLEMENTED YET_**
#### Attributes
| Attribute Name | Type  | Default Value | Description                                   |
|----------------|-------|---------------|-----------------------------------------------|
| database       | Class | None          | A pyoocass.Database instance                  |
| name           | str   | ""            | Name for the keyspace within the Cassandra DB |

#### Methods

### **Table**
**_NOT IMPLEMENTED YET_**
#### Attributes
| Attribute Name | Type  | Default Value | Description                                   |
|----------------|-------|---------------|-----------------------------------------------|
| keyspace       | Class | None          | A pyoocass.Keyspace instance                  |
| name           | str   | ""            | Name for the keyspace within the Cassandra DB |

#### Methods

## Code Examples
