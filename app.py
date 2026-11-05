
import streamlit as st
import pandas as pd
import json
import io

st.set_page_config(
    page_title="Data Chat App",
    layout="wide"
)

st.title("DataChatApp")
st.write("Upload and explore your CSV and JSON files.")

# Create storage for uploaded files
if "stored_files" not in st.session_state:
    st.session_state.stored_files = {}

if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0

# Upload files in batches
uploaded_files = st.file_uploader(
    "Upload CSV or JSON files",
    type=["csv", "json"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_version}"
)

# Save newly uploaded files in session memory
if uploaded_files:
    for file in uploaded_files:
        st.session_state.stored_files[file.name] = file.getvalue()

    # Reset uploader for the next batch
    st.session_state.uploader_version += 1
    st.rerun()

# Display all stored files
if st.session_state.stored_files:

    st.success(
        f"Total uploaded files: {len(st.session_state.stored_files)}"
    )

    for file_name, file_content in list(
        st.session_state.stored_files.items()
    ):

        with st.expander(file_name, expanded=True):

            try:
                if file_name.lower().endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(file_content))

                else:
                    data = json.loads(file_content)

                    if isinstance(data, list):
                        df = pd.json_normalize(data)

                    elif isinstance(data, dict):
                        if isinstance(data.get("data"), list):
                            df = pd.json_normalize(data["data"])
                        else:
                            df = pd.json_normalize(data)

                    else:
                        st.error("Unsupported JSON structure.")
                        continue

                st.dataframe(df, use_container_width=True)

                col1, col2 = st.columns(2)
                col1.metric("Rows", df.shape[0])
                col2.metric("Columns", df.shape[1])

            except Exception as e:
                st.error(f"Error reading file: {e}")

            # Remove individual files
            if st.button("Remove this file", key=f"remove_{file_name}"):
                del st.session_state.stored_files[file_name]
                st.rerun()

else:
    st.info("Please upload your CSV or JSON files.")