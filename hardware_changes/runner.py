from datetime import datetime, timedelta
from dotenv import dotenv_values
from pathlib import Path
import pandas as pd
import shutil
import json
import csv
import os

from utils.data_fetcher import fetch_data
from utils.queries import queries


def prepare_reports_directories(old_dir: Path, new_dir: Path) -> None:
    if not os.path.exists(old_dir):
        os.mkdir(old_dir)

    if not os.path.exists(new_dir):
        os.mkdir(new_dir)


def remove_files_from_directory(directory: Path) -> None:
    for file in os.listdir(directory):
        file_path = Path(directory, file)
        os.remove(file_path)


def move_csv_files(move_from: Path, move_to: Path) -> None:
    for file in os.listdir(move_from):
        if file.endswith(".csv"):
            shutil.move(
                src=Path(move_from, file),
                dst=move_to
            )


def generate_csv(directory: Path, document_name: str, data: list[tuple]) -> None:
    with open(Path(directory, f"{document_name}.csv"), "w", newline="") as file:
        writer = csv.writer(
            file,
            dialect="excel",
            quoting=csv.QUOTE_ALL
        )

        if "elds" in document_name:
            header = ["COMPANY NAME", "SERIAL NUMBER", "STATUS", "REPLACEMENT NOTE", "FORWARDED TO"]
        else:
            header = ["COMPANY NAME", "SERIAL NUMBER", "STATUS", "REPLACEMENT NOTE"]

        writer.writerow(header)
        for row in data:
            writer.writerow(row)


def generate_dataframe_from_csv(csv_doc: Path, index_col: str) -> pd.DataFrame:
    return pd.read_csv(filepath_or_buffer=csv_doc, on_bad_lines="skip", header=0, index_col=index_col).fillna("")


def fetch_csv_documents(directory: Path) -> list[Path]:
    return [Path(directory, file) for file in os.listdir(directory) if file.endswith(".csv")]


def fetch_xlsx_documents(directory: Path) -> list[Path]:
    return [Path(directory, file) for file in os.listdir(directory) if file.endswith(".xlsx")]


def compare_csv_data(old_dir: Path, new_dir: Path) -> None:
    for new_doc in fetch_csv_documents(directory=new_dir):
        file_name = new_doc.__str__().split("/")[1]

        old_doc = Path(old_dir, file_name)

        new_df = generate_dataframe_from_csv(csv_doc=new_doc, index_col="SERIAL NUMBER")
        old_df = generate_dataframe_from_csv(csv_doc=old_doc, index_col="SERIAL NUMBER")

        discrepancies = new_df[new_df.apply(tuple, axis=1).isin(old_df.apply(tuple, axis=1))]
        for_comparison = pd.DataFrame(columns=discrepancies.columns)

        for index in discrepancies.index:
            try:
                for_comparison = pd.concat([for_comparison, old_df.loc[[index]]])
            except KeyError:
                data = {}
                for col in discrepancies.columns:
                    data.update({col: ""})
                temp = pd.DataFrame(
                    data=data,
                    index=[index]
                )
                for_comparison = pd.concat([for_comparison, temp])

        result = for_comparison.compare(
            other=discrepancies,
            result_names=(str(datetime.now().date() - timedelta(1)), str(datetime.now().date()))
        )

        for index in result.index:
            result.loc[index, "CURRENT COMPANY NAME"] = new_df.at[index, "COMPANY NAME"]
            result.loc[index, "CURRENT STATUS"] = new_df.at[index, "STATUS"]
            result.loc[index, "CURRENT REPLACEMENT NOTE"] = new_df.at[index, "REPLACEMENT NOTE"]
            if str(index)[0:3] in ["87A", "87B", "87U", "88A", "88B", "88U"] or str(index)[0:2] in ["4C", "3B"]:
                result.loc[index, "CURRENT FORWARDED TO"] = new_df.at[index, "FORWARDED TO"]

        if not result.empty:
            result.fillna("").to_excel(Path(new_dir, f"{file_name.split(".")[0]}.xlsx"))


def main() -> None:
    env: dict = dotenv_values(dotenv_path=Path("..", ".env"))

    location_adapters: dict = json.loads(env.get("location_adapters"))
    databases: dict = json.loads(env.get("databases"))

    old_reports_dir: Path = Path("root", "runners", "daily_hardware_reports", "reports_old")
    new_reports_dir: Path = Path("root", "runners", "daily_hardware_reports", "reports_new")

    prepare_reports_directories(old_dir=old_reports_dir, new_dir=new_reports_dir)
    remove_files_from_directory(directory=old_reports_dir)
    move_csv_files(move_from=new_reports_dir, move_to=old_reports_dir)
    remove_files_from_directory(directory=new_reports_dir)

    for database, parameters in databases.items():
        eld_report_data: list[tuple] = fetch_data(
            query=queries.get("elds").format(
                *[url for platform, url in location_adapters.items()]
            ),
            params=parameters
        )

        gps_report_data: list[tuple] = fetch_data(
            query=queries.get("gps"),
            params=parameters
        )

        camera_report_data: list[tuple] = fetch_data(
            query=queries.get("cameras"),
            params=parameters
        )

        tablet_report_data: list[tuple] = fetch_data(
            query=queries.get("tablets"),
            params=parameters
        )

        generate_csv(
            directory=new_reports_dir,
            document_name=f"{database}_elds",
            data=eld_report_data
        )

        generate_csv(
            directory=new_reports_dir,
            document_name=f"{database}_gps",
            data=gps_report_data
        )

        generate_csv(
            directory=new_reports_dir,
            document_name=f"{database}_cameras",
            data=camera_report_data
        )

        generate_csv(
            directory=new_reports_dir,
            document_name=f"{database}_tablets",
            data=tablet_report_data
        )

    compare_csv_data(old_dir=old_reports_dir, new_dir=new_reports_dir)


if __name__ == "__main__":
    main()
