from dotenv import dotenv_values
from pathlib import Path
import requests
import urllib3
import json

BASE_DIR: Path = Path(Path(__file__).resolve().parent)
env: dict = dotenv_values(dotenv_path=Path(BASE_DIR, ".env"))


def get_session(url: str, password: str) -> requests.session:
    urllib3.disable_warnings()
    session: requests.session = requests.session()
    session.headers["content-type"] = "application/json"

    code_version: str = session.get(
        url=f"{url}/api/checkers/version",
        verify=False).text
    session.headers["codeVersion"] = code_version

    username: str = f"admin@{url.replace('https://', '').split('.', 1)[1]}" \
        if "eldrider" not in url else "admin@eldrider.us"

    token = session.post(
        url=f"{url}/web/login",
        data=json.dumps({"username": username, "password": password})
    ).json().get("token")

    session.headers["Authorization"] = f"Bearer {token}"

    return session


def close_session(session: requests.session, url: str) -> None:
    session.post(url=f"{url}/web/logout", verify=False)
    session.close()


def get_gps_devices(session: requests.session, url: str) -> dict:
    devices: dict = session.get(
        url=f"{url}/web/superAdmin/gpss?page=1&elements=9999&orderBy=serialNum&asc=true&status=active&"
            f"modelIds=d210%2Cd410%2Cd430%2Cgb130mg%2Cgl520mg%2Cgv620mg%2Cindash1508%2Cround1611%2Coval1711"
            f"%2Cthermo1802%2Cround2211%2CspireonTrailer%2CspireonTruck&manufacturer=anytrek&showUnassigned=true&"
            f"startTime=1546300800000&endTime=1733875200000&forceFinished=false&eventTypes=").json()

    return devices


def main() -> None:
    global env

    dev_password: str = env.get("dev_password")
    base_urls: dict = json.loads(
        s=env.get("base_urls"))

    gpss: list = []
    for app, base_url in base_urls.items():
        session: requests.session = get_session(url=base_url, password=dev_password)
        devices: dict = get_gps_devices(session=session, url=base_url).get("data")
        if devices:
            for gps in devices:
                if gps.get("manufacturer") == "anytrek" and gps.get("status") == "active":
                    sn: str = gps.get("serialNum")[0:14]
                    if sn not in gpss:
                        gpss.append(sn)
                    continue
        close_session(session=session, url=base_url)


if __name__ == "__main__":
    main()
