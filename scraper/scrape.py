import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
from notification import send_discord_message

# Load environment variables from .env file
load_dotenv()


# URL of GitHub's Trending page for repositories
BASE_URL = "https://github.com/trending"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

languages = [None, "Python", "JavaScript", "TypeScript", "Ruby", "Kotlin", "Rust", "Go"]
current_timestamp = datetime.now()
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d")


def main():
    # Create data folder if not
    # create_folder("data")
    full = pd.read_csv("data/github_daily_trending.csv")
    full = full.loc[:, ~full.columns.str.contains("^Unnamed")]
    dataframes = [full]
    for language in languages:
        language = language.lower() if language else language
        df, folder_name = extract_page_data(language)
        if df is not None:
            df["date"] = formatted_timestamp
            df["trending_category"] = language if language else "total"
            dataframes.append(df)
            # store_data(df, folder_name)
        else:
            send_discord_message(
                WEBHOOK_URL, "Something went wrong. Please check the log..."
            )

    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df.to_csv("data/github_daily_trending.csv", index=False)


def store_data(df, folder_name):
    new_folder = os.path.join("data", folder_name)
    create_folder(new_folder)
    current_timestamp = datetime.now()

    # Format the timestamp
    formatted_timestamp = current_timestamp.strftime("%Y-%m-%d")

    df.to_csv(f"{new_folder}/{formatted_timestamp}.csv", index=False)
    print(f"{new_folder}/{formatted_timestamp}.csv has been created")


def extract_page_data(filter):
    # Make a GET request to fetch the raw HTML content
    url = BASE_URL
    if filter:
        url = f"{url}/{filter}?since=daily"
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all repositories listed on the trending page
        trending_repos = soup.find_all("article", class_="Box-row")

        # Iterate over the repositories and extract details
        data = []
        for repo in trending_repos:  # Limiting to top 5 for example
            # Extract the repository name
            title = repo.h2.text.strip().replace("\n", "").replace(" ", "")
            org_name, repo_name = title.split("/")
            # Extract the repository URL
            repo_url = "https://github.com/" + title
            # Extract repository description
            description = repo.p.text.strip() if repo.p else "No description"

            # Extract Language
            language_tag = repo.find("span", {"itemprop": "programmingLanguage"})
            language = language_tag.text if language_tag else None
            # Extract the number of stars,forks (if available)
            star_tag = repo.find("a", {"href": f"/{title}/stargazers"})
            star = int(star_tag.text.strip().replace(",", "")) if star_tag else None

            forks_tag = repo.find("a", {"href": f"/{title}/forks"})
            forks = int(forks_tag.text.strip().replace(",", "")) if forks_tag else None
            daily_star_tag = repo.find_all("span")[-1]
            daily_star = (
                int(daily_star_tag.text.strip().split()[0].replace(",", ""))
                if daily_star_tag
                else None
            )

            data.append(
                {
                    "org_name": org_name,
                    "repo_name": repo_name,
                    "repo_url": repo_url,
                    "description": description,
                    "language": language,
                    "star": star,
                    "forks": forks,
                    "daily_star": daily_star,
                }
            )
        df = pd.DataFrame(data)
        folder_name = filter if filter else "total"
        return df, folder_name
    else:
        print(
            "Failed to retrieve the trending page. Status code:", response.status_code
        )
        return None, None


def create_folder(path):
    try:
        os.mkdir(path)
        print(f"Directory '{path}' created successfully.")
    except FileExistsError:
        None
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
