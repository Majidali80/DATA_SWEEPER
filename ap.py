import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in visualization!")

# File uploader for CSV and Excel files
uploaded_files = st.file_uploader(
    "Upload Your Files (CSV or Excel):",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# Dictionary to map file extensions to pandas read functions
readers = {
    ".csv": pd.read_csv,
    ".xlsx": pd.read_excel
}

if uploaded_files:
    for file in uploaded_files:
        # Extract file extension
        file_ext = os.path.splitext(file.name)[-1].lower()
        file_name = file.name

        # Get the appropriate reader function based on file extension
        read_func = readers.get(file_ext)
        if not read_func:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Read the file into a DataFrame
        try:
            df = read_func(file)
        except Exception as e:
            st.error(f"Error reading file {file_name}: {str(e)}")
            continue

        # Display file information
        st.write(f"**File Name:** {file_name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")

        # Display the first 5 rows of the DataFrame
        st.write("Preview the Head of the DataFrame")
        st.dataframe(df.head())

        # Data cleaning options
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file_name}"):
            col1, col2 = st.columns(2)

            # Remove duplicates
            with col1:
                if st.button(f"Remove Duplicates from {file_name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            # Fill missing values
            with col2:
                if st.button(f"Fill Missing Values for {file_name}"):
                    numeric_cols = df.select_dtypes(include="number").columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values Have Been Filled!")

        # Select specific columns to convert
        st.subheader("Select Columns to Convert")
        columns = st.multiselect(
            f"Choose Columns for {file_name}",
            options=df.columns,
            default=df.columns
        )
        df = df[columns]

        # Data visualization
        st.subheader("Data Visualization")
        if st.checkbox(f"Show Visualization for {file_name}"):
            numeric_data = df.select_dtypes(include="number").iloc[:, :2]
            if not numeric_data.empty:
                st.bar_chart(numeric_data)
            else:
                st.warning("No numeric columns available for visualization.")

        # File conversion options
        st.subheader("Conversion Options")
        conversion_type = st.radio(
            f"Convert {file_name} to:",
            options=["CSV", "Excel"],
            key=f"conversion_{file_name}"
        )

        if st.button(f"Convert {file_name}"):
            # Prepare the buffer for download
            buffer = BytesIO()
            mime_type = None

            # Convert and save to buffer based on the selected type
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                new_file_name = file_name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine="openpyxl")
                new_file_name = file_name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            # Download button
            st.download_button(
                label=f"Download {file_name} as {conversion_type}",
                data=buffer,
                file_name=new_file_name,
                mime=mime_type
            )

    # Success message after processing all files
    st.success("ALL FILES PROCESSED!")
else:
    st.info("Please upload a file to begin.")