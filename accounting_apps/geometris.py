import requests

from utils.lion_session_maker import make_lion_session, close_session
from dotenv import dotenv_values
from pathlib import Path
import csv

BASE_DIR: Path = Path(__file__).resolve().parent.parent
PROJECT_DIR: Path = Path(BASE_DIR, "accounting_apps")

BASE_URLS: dict[str, str] = {
    "xeld": "https://cloud.xeld.us",
    "eldrider": "https://eldrider.com",
    "optima": "https://web.optimaeld.com",
    "proride": "https://web.prorideeld.com",
    "xplore": "https://cloud.xploreeld.com",
    "sparkle": "https://web.sparkleeld.us",
    "txeld": "https://cloud.txeld.com",
    "eva": "https://cloud.evaeld.com",
    "apex": "https://cloud.apexeld.us",
    "rock": "https://cloud.rockeld.us",
    "peak": "https://cloud.eldpeak.com",
    "maestral": "https://web.eldmaestral.com",
    "pop": "https://cloud.popeld.com",
}


def get_geometris_devices(csv_file: Path) -> list[str]:
    """
    Loads geometris file. \n
    File structure is ["SERIAL", "ICCID", "Ship Date"] \n

    Makes a dictionary that contains ELD serial number as key and None for its value.

    :return: dict[str, None]
    """

    global PROJECT_DIR
    result: list[str] = []

    with open(
        file=csv_file,
        mode="r"
    ) as file:
        reader = csv.DictReader(file)
        for line in reader:
            eld_sn: str = line.get("SERIAL")
            result.append(eld_sn)

    return list(set(result))


def fetch_geometris_devices(password: str) -> list[str]:
    global BASE_URLS
    result: list[str] = []

    for platform, base_url in BASE_URLS.items():
        domain: str = base_url.split(".", 1)[1] if "eldrider" not in base_url else "eldrider.us"
        session: requests.session = make_lion_session(
            base_url=base_url,
            username=f"admin@{domain}",
            password=password
        )
        url: str = (f"{base_url}/web/superAdmin/elds?page=1&elements=99999&orderBy=serialNum&asc=true&"
                    f"status=active%2ConHold&manufacturer=geometris&showUnassigned=true&"
                    f"startTime=1546300800000&endTime=1740787200000&forceFinished=false&eventTypes=")
        devices = session.get(url=url).json().get("data")
        close_session(session=session, base_url=base_url)

        for device in devices:
            result.append(device.get("serialNum"))

    return list(set(result))


def main() -> None:
    global BASE_DIR
    global PROJECT_DIR

    env: dict = dotenv_values(
        dotenv_path=Path(BASE_DIR, ".env")
    )

    csv_file: Path = Path(PROJECT_DIR, "march_geometris.csv")

    geometris_devices: list[str] = get_geometris_devices(csv_file=csv_file)
    our_devices: list[str] = fetch_geometris_devices(password=env.get("dev_password"))

    print(f"{geometris_devices=}")
    print(f"{our_devices=}")

    result: list[str] = [device for device in geometris_devices if device not in our_devices]

    print(f"{result=}")


if __name__ == "__main__":
    main()
