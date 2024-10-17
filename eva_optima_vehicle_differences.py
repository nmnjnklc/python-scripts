from utils.data_fetcher import fetch_data
from utils.mail_sender import MailSender
from utils.queries import queries
from dotenv import dotenv_values
from pathlib import Path
import json


def get_transfer_in_progress_enabled_companies(connection_params: dict) -> list[dict]:
    return fetch_data(
        query=queries.get("transfer_in_progress_enabled_companies"),
        params=connection_params,
        as_dict=True
    )


def get_company_vehicles(company_name: str, connection_params: dict) -> list[dict]:
    return fetch_data(
        query=queries.get("vehicles_by_company_name").format(company_name),
        params=connection_params,
        as_dict=True
    )


def main() -> None:
    env: dict = dotenv_values(dotenv_path=Path(".env"))

    optima_params: dict = json.loads(s=env.get("local_optimaeld"))
    eva_params: dict = json.loads(s=env.get("local_evaeld"))

    ms: MailSender = MailSender(
        mail_username=env.get("mail_username"),
        mail_password=env.get("mail_password"))

    optima_transfer_in_progress_enabled_companies: list[dict] = get_transfer_in_progress_enabled_companies(
        connection_params=optima_params)

    result: list[dict] = []
    for company in optima_transfer_in_progress_enabled_companies:
        company_name: str = company.get("companyName")

        optima_vehicles: list[dict] = get_company_vehicles(
            company_name=company_name,
            connection_params=optima_params
        )

        eva_vehicles: list[dict] = get_company_vehicles(
            company_name=company_name,
            connection_params=eva_params
        )

        for vehicle in eva_vehicles:
            if vehicle.get("vin") not in [veh.get("vin") for veh in optima_vehicles]:
                vehicle.update({"companyName": company_name})
                result.append(vehicle)

    mail_to: list[str] = ["nnikolic@lioneight.com"]
    mail_subject: str = "EVA <> Optima vehicles checker"

    if result:
        rows: list[str] = [f"{v.get('companyName')}: {v.get('vehicleId')} - {v.get('vin')}" for v in result]
        ms.send_email_without_attachments(
            text="\n".join(rows),
            to=mail_to,
            subject=mail_subject
        )
    else:
        ms.send_email_without_attachments(
            text="There are no newly created vehicles on EVA ELD that are not already created on OptimaELD.",
            to=mail_to,
            subject=mail_subject
        )


if __name__ == "__main__":
    main()
