import os
import pandas as pd
import re

# Specify the folder path
folder_path = "../data/go"


def main():
    for filename in os.listdir("../data"):
        full_path = os.path.join("../data", filename)
        if not os.path.isfile(full_path):
            combine_df(full_path)
    dataframes = []
    for filename in os.listdir("../data"):
        full_path = os.path.join("../data", filename)
        if os.path.isfile(full_path):
            df = pd.read_csv(full_path)
            dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.to_csv("../data/github_daily_trending.csv", index=False)


def combine_df(folder_path):
    name = folder_path.split("/")[-1]
    dataframes = []
    pattern = r"\b\d{4}-\d{2}-\d{2}\b"

    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):  # Check if it is a file
            match = re.search(pattern, full_path)
            if match:
                df = pd.read_csv(full_path)
                df["date"] = match.group()
                df["trending_category"] = name
                dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)

    combined_df.to_csv(f"../data/{name}_combined.csv", index=False)


if __name__ == "__main__":
    main()
