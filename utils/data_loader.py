import pandas as pd


def load_data(uploaded_file):
    """
    Load CSV or Excel file into a pandas DataFrame.
    """

    if uploaded_file is None:
        return None

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        return pd.read_excel(uploaded_file)

    else:
        raise ValueError(
            "Unsupported file format. Please upload CSV or Excel."
        )


def clean_data(df):
    """
    Basic safe cleaning.
    """

    data = df.copy()

    # Remove completely empty rows
    data = data.dropna(how="all")

    # Remove completely empty columns
    data = data.dropna(axis=1, how="all")

    return data