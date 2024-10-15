import json
import time
import hashlib
import warnings
import pandas as pd
from pathlib import Path
from geopy import geocoders
from geopy.distance import geodesic
from datetime import datetime, timezone


#
# Implement logger !!!
#


def convert_str_date_to_datetime_object(date: str) -> datetime:
    tmp: list[int] = [int(n) for n in date.split("-")]
    dt: datetime = datetime(*tmp)

    return dt


def get_date(timestamp: int) -> str:
    dt: datetime = datetime.fromtimestamp(round(timestamp))
    readable_date: str = str(dt).split(" ")[0]

    return readable_date


def get_datemidnight_milliseconds(date: str) -> int:
    dt: datetime = convert_str_date_to_datetime_object(date=date)
    utc_datemidnight: int = int(dt.replace(
        hour=0, minute=0, second=0, tzinfo=timezone.utc
    ).timestamp()) * 1000

    return utc_datemidnight


def get_start_end_for_date(date: str) -> tuple:
    dt: datetime = convert_str_date_to_datetime_object(date=date)

    start: int = int(dt.replace(
        hour=12, minute=0, second=0
    ).timestamp()) * 1000

    end: int = int(dt.replace(
        hour=13, minute=0, second=0
    ).timestamp()) * 1000

    return start, end


def get_state(lat: float, lon: float, hashed_string: str) -> str:
    geolocator: geocoders = geocoders.Nominatim(user_agent=f"ifta_calculator_{hashed_string}")
    raw_output: geolocator = geolocator.reverse(
        query=(lat, lon),
        language="en"
    ).raw

    try:
        abbreviation: str = raw_output.get("address").get("ISO3166-2-lvl4").split("-")[1]
        if raw_output.get("address").get("state"):
            state: str = raw_output.get("address").get("state").upper().replace(" ", "_")
        else:
            state: str = raw_output.get("address").get("yes").upper().replace(" ", "_")

        return f"US_{abbreviation}_{state}"
    except Exception as e:
        print("*** From get_state function ***")
        print(f"{raw_output=}")
        print(f"Exception: {e}")
        raise e


def get_distance(a: tuple, b: tuple) -> float:
    return round(geodesic(a, b).miles, 1)


def get_hashed_string(to_hash: str) -> str:
    return hashlib.md5(to_hash.encode('UTF-8')).hexdigest()


def calculate_ifta(packets: pd.DataFrame) -> dict:
    result: dict = {}

    counter: int = 1
    data_length: int = len(packets)

    packets.index = list(range(1, data_length + 1))

    for index in packets.index:
        print(f"Calculating IFTA - working on {counter} of {data_length} packets...")

        if index > 1:
            if packets["MessageReason"][index] != "ON_PERIODIC":
                packets.drop(index=index)
                data_length -= 1
                continue

            hashed_string = get_hashed_string(str(round(datetime.now().timestamp())))
            if index % 10 == 0:
                hashed_string = get_hashed_string(str(packets["PacketTimeStamp"][index]))

            if index % 50 == 0:
                print("Sleeping for 5 seconds...")
                time.sleep(5)

            date: str = get_date(
                timestamp=packets["PacketTimeStamp"][index]
            )

            try:
                state: str = get_state(
                    lat=packets["Latitude"][index].item(),
                    lon=packets["Longitude"][index].item(),
                    hashed_string=hashed_string
                )
            except Exception as e:
                print(
                    f"Exception occurred: {e}",
                    f"For coordinates:",
                    f"Latitude: {packets["Latitude"][index].item()}",
                    f"Longitude: {packets["Longitude"][index].item()}",
                    sep="\n"
                )
                continue

            distance = get_distance(
                a=(packets["Latitude"][index - 1].item(), packets["Longitude"][index - 1].item()),
                b=(packets["Latitude"][index].item(), packets["Longitude"][index].item())
            )

            if not result.get(date):
                result.update(
                    {date: {
                        "ifta": {}
                    }})

            if not result.get(date).get("ifta").get(state):
                result[date]["ifta"].update(
                    {state: 0}
                )

            result[date]["ifta"][state] = round(result[date]["ifta"][state] + distance, 1)

            counter += 1

    return result


def populate_ifta_with_metadata(ifta: dict):
    result: dict = ifta
    result_keys: list = list(result.keys())

    for key in result_keys:
        start, end = get_start_end_for_date(date=key)

        result[key].update(
            {"meta": {
                "dateMidnight": get_datemidnight_milliseconds(date=key),
                "start": start,
                "end": end
            }})

    return result


def save_to_json(result: dict, file_path: Path, file_name: str) -> None:
    with open(Path(file_path, f"{file_name}.json"), "w") as file:
        file.write(json.dumps(result, indent=4))


def main() -> None:
    warnings.simplefilter(action="ignore", category=Warning)

    csv_document: Path = Path("Users", "nemanja", "Downloads", "87B010210022_new.csv")

    df: pd.DataFrame = pd.read_csv(csv_document, on_bad_lines="skip")
    data: pd.DataFrame = df[["PacketTimeStamp", "MessageReason", "Latitude", "Longitude"]]

    calculated_ifta: dict = calculate_ifta(packets=data)

    final_ifta: dict = populate_ifta_with_metadata(ifta=calculated_ifta)

    save_to_json(result=final_ifta, file_path=Path("."), file_name="result.json")


if __name__ == "__main__":
    main()
