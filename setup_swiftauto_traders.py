#!/usr/bin/env python

"""
SCRIPT: setup_swiftauto_traders.py
AUTHOR: Pravin Regismond
DATE: 2024-10-12
DESCRIPTION: This script automates the setup of the Snowflake environment
             for this project. It handles the uploading of CSV dataset files
             to stage, creates and loads tables with inferred schemas, and
             establishes a basic role hierarchy and user setup to demonstrate
             dashboard sharing within Snowflake.

AUDIT TRAIL START                               INIT  DATE
----------------------------------------------  ----- -----------
1. Initial version                              PR    2024-10-12
2. Added COMMENT property for CREATE OR         PR    2024-11-17
   REPLACE USER statements for documentation.
3. Added DATA_ANALYST functional role for       PR    2024-11-18
   documentation.

AUDIT TRAIL END
"""

# Importing the required libraries
import os
import glob
import snowflake.connector as sf
from snowflake.connector.errors import ProgrammingError


def get_snowflake_connection():
    """
    Establish a connection to Snowflake using SYSADMIN role.

    Returns:
        snowflake.connector.connection.SnowflakeConnection:
            Snowflake connection object
    """
    return sf.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        role='SYSADMIN'
    )


def print_environment_details(cursor):
    """
    Print current environment details.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    cursor.execute(
        """
        SELECT current_user(), current_role(), current_database(),
               current_schema(), current_warehouse(), current_version(),
               current_client();
        """
    )
    snowflake_env = cursor.fetchone()

    print("Current Environment Details:")
    print("---------------------------------")
    print(f"User                        : {snowflake_env[0]}")
    print(f"Role                        : {snowflake_env[1]}")
    print(f"Database                    : {snowflake_env[2]}")
    print(f"Schema                      : {snowflake_env[3]}")
    print(f"Warehouse                   : {snowflake_env[4]}")
    print(f"Snowflake version           : {snowflake_env[5]}")
    print(
        f"Snowflake Connector for Python version: "
        f"{snowflake_env[6].split()[-1]}"
    )
    print("---------------------------------")


def create_warehouse(cursor):
    """
    Create warehouse SWIFTAUTO_WH.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    try:
        cursor.execute(
            """
            CREATE WAREHOUSE IF NOT EXISTS SWIFTAUTO_WH
            WITH WAREHOUSE_SIZE = 'XSMALL'
            AUTO_SUSPEND = 300
            AUTO_RESUME = TRUE;
            """
        )
        print("Warehouse SWIFTAUTO_WH created or already exists.")

        cursor.execute("USE WAREHOUSE SWIFTAUTO_WH;")
        print("Using warehouse SWIFTAUTO_WH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_database(cursor):
    """
    Create database SWIFTAUTO_DB.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS SWIFTAUTO_DB;")
        print("Database SWIFTAUTO_DB created or already exists.")

        cursor.execute("USE DATABASE SWIFTAUTO_DB;")
        print("Using database SWIFTAUTO_DB.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_schema(cursor):
    """
    Create schema SWIFTAUTO_DB.AUTOMOTIVE.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    try:
        cursor.execute(
            """
            CREATE SCHEMA IF NOT EXISTS SWIFTAUTO_DB.AUTOMOTIVE;
            """
        )
        print("Schema SWIFTAUTO_DB.AUTOMOTIVE created or already exists.")

        cursor.execute("USE SCHEMA SWIFTAUTO_DB.AUTOMOTIVE;")
        print("Using schema SWIFTAUTO_DB.AUTOMOTIVE.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_stage(cursor):
    """
    Create stage SWIFTAUTO_DB.PUBLIC.AUTOMOTIVE_INDUSTRY.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    try:
        cursor.execute(
            """
            CREATE STAGE IF NOT EXISTS
            SWIFTAUTO_DB.PUBLIC.AUTOMOTIVE_INDUSTRY;
            """
        )
        print(
            "Stage SWIFTAUTO_DB.PUBLIC.AUTOMOTIVE_INDUSTRY created or "
            "already exists."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def upload_csv_files(cursor, file_location):
    """
    Upload CSV files to the stage.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
        file_location (str): Path to the directory containing CSV files.
    """
    try:
        for csvfile in glob.glob(os.path.join(file_location, "*.csv")):
            cursor.execute(
                f"""
                PUT file://{csvfile}
                @SWIFTAUTO_DB.PUBLIC.AUTOMOTIVE_INDUSTRY
                AUTO_COMPRESS = FALSE
                OVERWRITE = TRUE;
                """
            )
            print(f"Uploaded {csvfile} to stage.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_tables(cursor):
    """
    Create and load tables with inferred schema.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    try:
        # Create a file format for CSV
        cursor.execute(
            """
            CREATE OR REPLACE FILE FORMAT SWIFTAUTO_DB.PUBLIC.CSV_FF
                TYPE = CSV
                PARSE_HEADER = TRUE
                FIELD_DELIMITER = ','
                TRIM_SPACE = TRUE
                FIELD_OPTIONALLY_ENCLOSED_BY = '\042'
                NULL_IF = ('\\N', 'NULL', '')
                EMPTY_FIELD_AS_NULL = TRUE
                ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE;
            """
        )
        print("Created or replaced file format SWIFTAUTO_DB.PUBLIC.CSV_FF.")

        # Execute the LIST command to get files in the stage
        cursor.execute(
            """
            LIST @SWIFTAUTO_DB.PUBLIC.AUTOMOTIVE_INDUSTRY/;
            """
        )

        # Fetch all files and extract file names
        files = cursor.fetchall()
        file_names = [file[0].split('/')[-1] for file in files]

        # Loop through each CSV file and create a table
        for csvfile in file_names:
            table_name = csvfile.split(".")[0].upper()
            print(f"Creating table {table_name} using detected schema:")

            # Create table statement using template
            create_table_query = (
                f"""
                CREATE OR REPLACE TABLE {table_name} USING TEMPLATE (
                    SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                    FROM TABLE(
                        INFER_SCHEMA(
                            LOCATION =>
                            '@SWIFTAUTO_DB.PUBLIC.AUTOMOTIVE_INDUSTRY/{csvfile}',
                            FILE_FORMAT => 'SWIFTAUTO_DB.PUBLIC.CSV_FF',
                            IGNORE_CASE => TRUE
                        )
                    )
                );
                """
            )
            print(create_table_query)

            # Execute the SQL command
            cursor.execute(create_table_query)
            print(f"Table {table_name} created.")

            # Load the CSV file using MATCH_BY_COLUMN_NAME
            cursor.execute(
                f"""
                COPY INTO {table_name}
                FROM @SWIFTAUTO_DB.PUBLIC.AUTOMOTIVE_INDUSTRY/{csvfile}
                FILE_FORMAT = (
                    FORMAT_NAME = 'SWIFTAUTO_DB.PUBLIC.CSV_FF'
                )
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
                """
            )
            print(f"Data loaded into table {table_name} from {csvfile}.")

            # Rename columns to replace spaces with underscores
            cursor.execute(
                f"""
                SELECT COLUMN_NAME
                FROM SWIFTAUTO_DB.INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}';
                """
            )
            columns = cursor.fetchall()

            for col in columns:
                original_col = col[0]
                modified_col = original_col.replace(" ", "_")
                if original_col != modified_col:
                    cursor.execute(
                        f"""
                        ALTER TABLE {table_name}
                        RENAME COLUMN "{original_col}" TO "{modified_col}";
                        """
                    )
                    print(
                        f"Renamed column {original_col} to {modified_col} in "
                        f"table {table_name}."
                    )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def create_roles(cursor):
    """
    Create a role hierarchy.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    sql_commands = [
        "USE ROLE SECURITYADMIN;",
        "CREATE ROLE IF NOT EXISTS SWIFTAUTO_BI_CREATOR_ROLE "
        "COMMENT = 'Access role that permits BI creator access for "
        "SWIFTAUTO_DB';",
        "CREATE ROLE IF NOT EXISTS SWIFTAUTO_BI_VIEWER_ROLE "
        "COMMENT = 'Access role that permits BI viewer access for "
        "SWIFTAUTO_DB';",
        "CREATE ROLE IF NOT EXISTS SWIFTAUTO_READ_ROLE "
        "COMMENT = 'Access role that permits read-only access for "
        "SWIFTAUTO_DB';",
        "CREATE ROLE IF NOT EXISTS SWIFTAUTO_READWRITE_ROLE "
        "COMMENT = 'Access role that permits read-write access for "
        "SWIFTAUTO_DB';",
        "CREATE ROLE IF NOT EXISTS DATA_ANALYST "
        "COMMENT = 'Functional role for data analysts';",
        "CREATE ROLE IF NOT EXISTS DATA_SCIENTIST "
        "COMMENT = 'Functional role for data scientists';",
        "CREATE ROLE IF NOT EXISTS REGIONAL_MANAGER "
        "COMMENT = 'Functional role for regional managers';",
        "GRANT ROLE SWIFTAUTO_READ_ROLE TO ROLE DATA_ANALYST;",
        "GRANT ROLE SWIFTAUTO_BI_CREATOR_ROLE TO ROLE DATA_SCIENTIST;",
        "GRANT ROLE SWIFTAUTO_BI_VIEWER_ROLE TO ROLE DATA_SCIENTIST;",
        "GRANT ROLE SWIFTAUTO_READWRITE_ROLE TO ROLE DATA_SCIENTIST;",
        "GRANT ROLE SWIFTAUTO_BI_VIEWER_ROLE TO ROLE REGIONAL_MANAGER;",
        "GRANT ROLE DATA_ANALYST, DATA_SCIENTIST, REGIONAL_MANAGER "
        "TO ROLE SYSADMIN;",
        "GRANT USAGE, MONITOR ON WAREHOUSE SWIFTAUTO_WH "
        "TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;",
        "GRANT USAGE ON WAREHOUSE SWIFTAUTO_WH "
        "TO ROLE SWIFTAUTO_BI_VIEWER_ROLE;",
        "GRANT USAGE ON WAREHOUSE SWIFTAUTO_WH "
        "TO ROLE SWIFTAUTO_READ_ROLE;",
        "GRANT USAGE ON WAREHOUSE SWIFTAUTO_WH "
        "TO ROLE SWIFTAUTO_READWRITE_ROLE;",
        "GRANT USAGE ON DATABASE SWIFTAUTO_DB "
        "TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;",
        "GRANT USAGE ON DATABASE SWIFTAUTO_DB "
        "TO ROLE SWIFTAUTO_BI_VIEWER_ROLE;",
        "GRANT USAGE ON DATABASE SWIFTAUTO_DB "
        "TO ROLE SWIFTAUTO_READ_ROLE;",
        "GRANT USAGE ON DATABASE SWIFTAUTO_DB "
        "TO ROLE SWIFTAUTO_READWRITE_ROLE;",
        "GRANT USAGE ON SCHEMA SWIFTAUTO_DB.AUTOMOTIVE "
        "TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;",
        "GRANT USAGE ON SCHEMA SWIFTAUTO_DB.AUTOMOTIVE "
        "TO ROLE SWIFTAUTO_BI_VIEWER_ROLE;",
        "GRANT USAGE ON SCHEMA SWIFTAUTO_DB.AUTOMOTIVE "
        "TO ROLE SWIFTAUTO_READ_ROLE;",
        "GRANT USAGE ON SCHEMA SWIFTAUTO_DB.AUTOMOTIVE "
        "TO ROLE SWIFTAUTO_READWRITE_ROLE;",
        "GRANT SELECT ON ALL TABLES IN SCHEMA SWIFTAUTO_DB.AUTOMOTIVE "
        "TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;",
        "GRANT SELECT ON ALL TABLES IN SCHEMA SWIFTAUTO_DB.AUTOMOTIVE "
        "TO ROLE SWIFTAUTO_BI_VIEWER_ROLE;",
        "GRANT SELECT ON ALL TABLES IN SCHEMA SWIFTAUTO_DB.AUTOMOTIVE "
        "TO ROLE SWIFTAUTO_READ_ROLE;",
        "GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON ALL TABLES "
        "IN SCHEMA SWIFTAUTO_DB.AUTOMOTIVE TO ROLE SWIFTAUTO_READWRITE_ROLE;",
        "GRANT USAGE ON SCHEMA SWIFTAUTO_DB.PUBLIC "
        "TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;",
        "GRANT USAGE ON SCHEMA SWIFTAUTO_DB.PUBLIC "
        "TO ROLE SWIFTAUTO_BI_VIEWER_ROLE;",
        "GRANT CREATE STREAMLIT ON SCHEMA SWIFTAUTO_DB.PUBLIC "
        "TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;",
        "GRANT CREATE STAGE ON SCHEMA SWIFTAUTO_DB.PUBLIC "
        "TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;",
        "USE ROLE ACCOUNTADMIN;",
        "GRANT CREATE SHARE ON ACCOUNT TO ROLE SWIFTAUTO_BI_CREATOR_ROLE;"
    ]

    # Execute each SQL command individually
    for command in sql_commands:
        try:
            print(f"Executing command: {command}")
            cursor.execute(command)
        except ProgrammingError as pe:
            print(f"Error executing command: {command}\n{pe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def create_users(cursor):
    """
    Create users and grant functional roles.

    Args:
        cursor (snowflake.connector.cursor.SnowflakeCursor):
            Snowflake cursor object.
    """
    sql_commands = [
        "USE ROLE USERADMIN;",
        "CREATE OR REPLACE USER RM_DENVER "
        "PASSWORD = 'abc123' "
        "COMMENT = 'Regional Manager, Denver, Colorado' "
        "MUST_CHANGE_PASSWORD = TRUE "
        "DEFAULT_WAREHOUSE = SWIFTAUTO_WH;",
        "CREATE OR REPLACE USER DS_JSMITH "
        "PASSWORD = 'abc123' "
        "COMMENT = 'Data Scientist, SwiftAuto Traders' "
        "MUST_CHANGE_PASSWORD = TRUE "
        "DEFAULT_WAREHOUSE = SWIFTAUTO_WH;",
        "USE ROLE SECURITYADMIN;",
        "GRANT ROLE REGIONAL_MANAGER TO USER RM_DENVER;",
        "GRANT ROLE DATA_SCIENTIST TO USER DS_JSMITH;",
        "ALTER USER RM_DENVER SET DEFAULT_ROLE = REGIONAL_MANAGER;",
        "ALTER USER DS_JSMITH SET DEFAULT_ROLE = DATA_SCIENTIST;"
    ]

    # Execute each SQL command individually
    for command in sql_commands:
        try:
            print(f"Executing command: {command}")
            cursor.execute(command)
        except ProgrammingError as pe:
            print(f"Error executing command: {command}\n{pe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def main():
    """
    Main function to execute the Snowflake operations.
    """
    ctx = get_snowflake_connection()
    cs = ctx.cursor()
    try:
        create_warehouse(cs)
        create_database(cs)
        create_schema(cs)
        print_environment_details(cs)
        create_stage(cs)
        upload_csv_files(cs, "./Automotive_Industry/")
        create_tables(cs)
        create_roles(cs)
        create_users(cs)
    finally:
        # Close the cursor and connection
        cs.close()
        ctx.close()


if __name__ == "__main__":
    main()
