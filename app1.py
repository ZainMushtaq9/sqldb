import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "sap_b1_mock.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def get_table_names(conn):
    """Retrieves a list of all table names in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table['name'] for table in tables]

def fetch_table_data(conn, table_name, limit=1000):
    """Fetches data from a specified table."""
    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit};"
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error fetching data from table {table_name}: {e}")
        return pd.DataFrame()

def execute_custom_query(conn, query):
    """Executes a custom SQL query."""
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error executing custom query: {e}")
        return pd.DataFrame()

st.set_page_config(layout="wide", page_title="SAP B1 Mock DB Viewer")

st.title("SAP B1 Mock Database Viewer (Pakistani Data)")

# Database connection
conn = get_db_connection()

# Sidebar for navigation
st.sidebar.header("Navigation")
selected_option = st.sidebar.radio("Choose an option:", ("Browse Tables", "Custom SQL Query"))

if selected_option == "Browse Tables":
    st.header("Browse Database Tables")

    tables = get_table_names(conn)
    if not tables:
        st.warning("No tables found in the database. Please ensure the database is populated.")
    else:
        selected_table = st.selectbox("Select a table to view:", tables)
        data_limit = st.slider("Number of rows to display:", 100, 10000, 1000)

        if st.button(f"Load Data from {selected_table}"):
            df = fetch_table_data(conn, selected_table, limit=data_limit)
            if not df.empty:
                st.write(f"Displaying first {len(df)} rows from '{selected_table}':")
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"No data found or an error occurred for table '{selected_table}'.")

elif selected_option == "Custom SQL Query":
    st.header("Execute Custom SQL Query")
    st.info("Use this section to execute your own SQL queries. Be careful with UPDATE/DELETE/DROP statements.")

    query_input = st.text_area("Enter your SQL query here:", height=150, value="SELECT * FROM OUSR LIMIT 10;")

    if st.button("Execute Query"):
        if query_input.strip():
            df = execute_custom_query(conn, query_input)
            if not df.empty:
                st.write("Query Results:")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Query executed, but no results returned or an error occurred.")
        else:
            st.warning("Please enter a SQL query.")

conn.close()