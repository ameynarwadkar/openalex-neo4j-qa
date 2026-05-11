import json
import time
import requests
from tqdm import tqdm

TOPIC = "neuro-symbolic AI"
TARGET = 500
PER_PAGE = 200

OUTPUT_FILE = "openalex_works.json"


def fetch_openalex_works():
    works = []
    cursor = "*"

    with tqdm(total=TARGET, desc="Fetching OpenAlex papers") as pbar:
        while len(works) < TARGET:
            url = "https://api.openalex.org/works"

            params = {
                "search": TOPIC,
                "per-page": PER_PAGE,
                "cursor": cursor,
                "select": (
                    "id,doi,title,publication_year,"
                    "authorships,concepts,primary_location,referenced_works"
                ),
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            remaining = TARGET - len(works)
            selected_results = results[:remaining]
            works.extend(selected_results)

            pbar.update(len(selected_results))

            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break

            time.sleep(0.2)

    return works


def main():
    works = fetch_openalex_works()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(works, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(works)} papers to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()