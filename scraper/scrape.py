import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# URL of GitHub's Trending page for repositories
BASE_URL = "https://github.com/trending"

languages = [None, "Python", "JavaScript", "TypeScript", "Ruby", "Kotlin", "Rust", "Go"]


def main():
    # Create data folder if not
    create_folder("data")
    for language in languages:
        language = language.lower() if language else language
        df, folder_name = extract_page_data(language)
        if df is not None:
            store_data(df, folder_name)


def store_data(df, folder_name):
    new_folder = os.path.join("data", folder_name)
    create_folder(new_folder)
    current_timestamp = datetime.now()

    # Format the timestamp
    formatted_timestamp = current_timestamp.strftime("%Y-%m-%d")

    df.to_csv(f"{new_folder}/{formatted_timestamp}.csv", index=False)


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
            language = repo.find("span", {"itemprop": "programmingLanguage"}).text
            # Extract the number of stars,forks (if available)
            star = (
                repo.find("a", {"href": f"/{title}/stargazers"})
                .text.strip()
                .replace(",", "")
            )
            star = int(star)
            forks = (
                repo.find("a", {"href": f"/{title}/forks"})
                .text.strip()
                .replace(",", "")
            )
            forks = int(forks)
            daily_star = (
                repo.find_all("span")[-1].text.strip().split()[0].replace(",", "")
            )
            daily_star = int(daily_star)

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
        return None


def create_folder(path):
    try:
        os.mkdir(path)
        print(f"Directory '{path}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
