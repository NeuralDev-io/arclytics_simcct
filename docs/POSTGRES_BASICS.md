# PostgreSQL Basic Syntax

## Common PostgrSQL Commands

[1] <http://www.emblocsoft.com/About/PG/Useful-PostgreSQL-commands>



| Command                | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `\h [NAME]`            | help on syntax of SQL commands, * for all commands           |
| `\cd [DIR]`            | change the current working directory                         |
| `\c [DBNAME]`          | connect to new database (currently "postgres") / **use database** |
| `\p`                   | show the contents of the query buffer                        |
| `\s [FILE]`            | display history or save it to file                           |
| `\i FILE`              | execute commands from file                                   |
| `\ir FILE`             | as `\i`, but relative to location of current script          |
| `\d`                   | list tables / **show tables** (Schema \| Name \| Type \| Owner) |
| `\dS`                  | list tables and views / show views (Schema \| Name \| Type \| Owner) |
| `\dt`                  | list tables / **show tables**                                |
| `\dTS`                 | list data types / **show data types**                        |
| `\ds`                  | list relations /**show schema** (Schema \| Name \| Type \| Owner \| Size \| Description) |
| `\du`                  | list roles / **show users** / **show roles**                 |
| `\l`                   | list all databases  / **show database**                      |
| `\password [USERNAME]` | securely change the password for a user                      |



## Common SQL Commands

| Command                  | Description                                             | Sample                                                       |
| ------------------------ | ------------------------------------------------------- | ------------------------------------------------------------ |
| ALTER DATABASE           | change a database                                       | ALTER DATABASE name OWNER TO new_owner;                      |
| ALTER DEFAULT PRIVILEGES | define default access privileges                        | postgres=# \h ALTER DEFAULT PRIVILEGES                       |
| ALTER ROLE               | change a database role                                  | ALTER ROLE name RENAME TO new_name                           |
| ALTER TABLE              | change the definition of a table                        | postgres=# \h ALTER TABLE                                    |
| ALTER USER               | change a database role                                  | postgres=# \h ALTER USER                                     |
| BEGIN                    | start a transaction block                               | postgres=# BEGIN ;                                           |
| CHECKPOINT               | force a transaction log checkpoint                      | postgres=# CHECKPOINT;                                       |
| COMMIT                   | commit the current transaction                          | COMMIT TRANSACTION;                                          |
| COPY                     | copy data between a file and a table                    | postgres=# \h COPY                                           |
| CREATE DATABASE          | **create a new database**                               |                                                              |
| CREATE ROLE              |                                                         |                                                              |
| CREATE SCHEMA            |                                                         |                                                              |
| CREATE TABLE             |                                                         |                                                              |
| CREATE USER              | **create a new user**                                   |                                                              |
| CREATE VIEW              |                                                         |                                                              |
| DELETE                   | delete rows of a table                                  | postgres=# \h DELETE                                         |
| DROP DATABASE            |                                                         |                                                              |
| DROP ROLE                |                                                         |                                                              |
| DROP SCHEMA              |                                                         |                                                              |
| DROP TABLE               |                                                         |                                                              |
| DROP USER                |                                                         |                                                              |
| DROP VIEW                |                                                         |                                                              |
| GRANT                    | define access privileges                                |                                                              |
| INSERT                   | create new rows in a table                              |                                                              |
| REVOKE                   | remove access privileges                                | postgres=# \h REVOKE                                         |
| ROLLBACK                 | abort the current transaction                           | ROLLBACK [ WORK \| TRANSACTION ]                             |
| SELECT                   | retrieve rows from a table or view                      |                                                              |
| SELECT INTO              | define a new table from the results of a query          | postgres=# \h SELECT INTO                                    |
| SET                      | change a run-time parameter                             | postgres=# \h SET                                            |
| SET CONSTRAINTS          | set constraint check timing for the current transaction | SET CONSTRAINTS { ALL \| name [, ...] } { DEFERRED \| IMMEDIATE } |
| SET ROLE                 | set the current user identifier of the current session  | SET [ SESSION \| LOCAL ] ROLE role_name SET [ SESSION \| LOCAL ] ROLE NONE RESET ROLE |
| TABLE                    | retrieve rows from a table or view                      | postgres=# \h TABLE                                          |
| UPDATE                   | update rows of a table                                  | postgres=# \h UPDATE                                         |
| WITH                     | retrieve rows from a table or view                      | postgres=# \h WITH                                           |

