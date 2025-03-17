import requests


CLOUDFLARE_URLS: dict[str, str] = {
    "unresolved-incidents": "https://www.cloudflarestatus.com/api/v2/incidents/unresolved.json",
    "upcoming-scheduled-maintenances": "https://www.cloudflarestatus.com/api/v2/scheduled-maintenances/upcoming.json"
}


def get_incidents() -> list[dict] | None:
    global CLOUDFLARE_URLS

    incidents = requests.get(url=CLOUDFLARE_URLS.get("unresolved-incidents"))
    if not incidents.status_code == 200:
        return None

    return incidents.json().get("incidents")


def get_scheduled_maintenances() -> list[dict] | None:
    global CLOUDFLARE_URLS

    maintenances = requests.get(url=CLOUDFLARE_URLS.get("upcoming-scheduled-maintenances"))
    if not maintenances.status_code == 200:
        return None

    return maintenances.json().get("scheduled_maintenances")
