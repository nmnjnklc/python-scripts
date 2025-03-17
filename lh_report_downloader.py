from utils.lion_session_maker import make_lion_session, close_session
from dotenv import dotenv_values
from datetime import datetime
from pathlib import Path


import requests
import json
import csv


def ms_to_str(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0).strftime("%b %d, %I:%M %p")


def get_company_data(
        session: requests.session,
        base_url: str,
        company_name: str
) -> tuple[dict, list[dict], list[dict]]:
    company_data: dict = session.get(
        url=f"{base_url}/web/fleetManagement/companies?page=1&elements=25&orderBy=companyName&asc=true"
            f"&quickSearch={company_name.replace(' ', '%20')}&showUnassigned=true&startTime=1735689600000"
            f"&endTime=1776294400000&forceFinished=false&eventTypes=&optionIds="
    ).json().get("data")[0]

    groups: list[dict] = session.post(
        url=f"{base_url}/web/fleetManagement/groups?page=1&elements=9999&orderBy=name&asc=true&showUnassigned=true"
            f"&startTime=1735689600000&endTime=1736294400000&forceFinished=false&eventTypes=&"
            f"companyIds=&groupIds=&vehicleIds=&driverIds=&fmIds=&trailerIds=",
        data=json.dumps({"companyIds": ["allc"], "groupIds": ["allg"]})
    ).json().get("data")

    company_groups: list[dict] = [group for group in groups if group.get("companyId") == company_data.get("id")]

    company_vehicles = session.post(
        url=f"{base_url}/web/reports/vehicle/extras?companyIds=&groupIds=&vehicleIds=&driverIds=&fmIds=&trailerIds=",
        data=json.dumps(
            {"companyIds": [company_data.get("id")], "groupIds": [group.get("id") for group in company_groups]})
    ).json().get("vehicles")

    return company_data, company_groups, company_vehicles


def get_lh_report(
        session: requests.session,
        base_url: str,
        is_static: bool,
        start_time: int,
        end_time: int,
        vehicle: str,
        company_ids: list[str],
        group_ids: list[str],
        vehicle_ids: list[str]
) -> list[dict]:
    static: str = "true" if is_static else "false"
    report = session.post(
        url=f"{base_url}/web/reports/locationHistory/{vehicle}?page=1&elements=99999999&orderBy=date&asc=true"
            f"&showUnassigned=true&startTime={start_time}&endTime={end_time}&vehicleIds="
            f"&state=US_AL%2CUS_AK%2CUS_AZ%2CUS_AR%2CUS_CA%2CUS_CO%2CUS_CT%2CUS_DE%2CUS_DC%2CUS_FL%2CUS_GA%2CUS_HI%2C"
            f"US_ID%2CUS_IL%2CUS_IN%2CUS_IA%2CUS_KS%2CUS_KY%2CUS_LA%2CUS_ME%2CUS_MD%2CUS_MA%2CUS_MI%2CUS_MN%2CUS_MS%2C"
            f"US_MO%2CUS_MT%2CUS_NE%2CUS_NV%2CUS_NH%2CUS_NJ%2CUS_NM%2CUS_NY%2CUS_NC%2CUS_ND%2CUS_OH%2CUS_OK%2CUS_OR%2C"
            f"US_PA%2CUS_RI%2CUS_SC%2CUS_SD%2CUS_TN%2CUS_TX%2CUS_UT%2CUS_VT%2CUS_VA%2CUS_WA%2CUS_WV%2CUS_WI%2CUS_WY"
            f"&forceFinished=false&eventTypes=&companyIds=&groupIds=&optionIds="
            f"&staticLh={static}&driverIds=&fmIds=&trailerIds=",
        data=json.dumps({"companyIds": company_ids, "groupIds": group_ids, "vehicleIds": vehicle_ids}))
    return report.json().get("data")


def main() -> None:
    env: dict = dotenv_values(
        dotenv_path=Path(Path(__name__).resolve().parent, ".env"))

    base_url: str = env.get("base_url")
    company_name: str = "Roland Logistics Inc"
    vehicles: list[str] | None = None
    start_time: int = 1736640000000  # UTC timezone
    end_time: int = 1736640000000    # UTC timezone

    session: requests.session = make_lion_session(
        base_url=base_url,
        username="companieseld@gmail.com",
        password=env.get("dev_password"))

    company_data, company_groups, company_vehicles = get_company_data(
        session=session, base_url=base_url, company_name=company_name)
    
    counter: int = 1
    for vehicle in company_vehicles:
        print(f"Working on {counter} of {len(company_vehicles)}...")
        report: list[dict] = get_lh_report(
            session=session,
            base_url=base_url,
            is_static=True,
            start_time=start_time,
            end_time=end_time,
            vehicle=vehicle.get("id"),
            company_ids=[company_data.get("id")],
            group_ids=[group.get("id") for group in company_groups],
            vehicle_ids=[vehicle.get("id")])
        sorted_report: list[dict] = sorted(report, key=lambda d: d["date"])
        with open(f"csvs/{company_name} {vehicle.get("name")}.csv", "w") as csv_file:
            writer = csv.writer(csv_file)
            c: int = 0
            for row in sorted_report:
                row["date"] = ms_to_str(row["date"])
                header = row.keys()
                if c == 0:
                    writer.writerow(header)
                    c += 1
                writer.writerow(row.values())
        counter += 1

    close_session(session=session, base_url=base_url)


if __name__ == "__main__":
    main()
