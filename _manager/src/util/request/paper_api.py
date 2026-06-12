import requests


def get_latest_paper_version() -> str:
    try:
        headers = {
            "User-Agent": "my-server-manager/1.0 ([email protected])"
        }

        response = requests.get(
            "https://fill.papermc.io/v3/projects/paper",
            headers=headers
        )

        data = response.json()

        latest_version = next(iter(data["versions"].values()))[0]

        return latest_version
    except Exception as e:
        return None