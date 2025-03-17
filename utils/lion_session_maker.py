import requests
import urllib3
import json


def make_lion_session(base_url: str, username: str, password: str) -> requests.session:
    print(f"Opening session for {base_url}")
    urllib3.disable_warnings()

    session: requests.session = requests.session()
    session.headers["content-type"] = "application/json"

    code_version: str = session.get(
            url=f"{base_url}/api/checkers/version",
            verify=False).text
    session.headers["codeVersion"] = code_version

    token: str = session.post(
        url=f"{base_url}/web/login",
        data=json.dumps({"username": username, "password": password})
    ).json().get("token")

    session.headers["Authorization"] = f"Bearer {token}"

    return session


def close_session(session: requests.session, base_url: str) -> None:
    print(f"Closing session for {base_url}")

    session.post(url=f"{base_url}/web/logout", verify=False)
    session.close()
