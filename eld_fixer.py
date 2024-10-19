from urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta
from dotenv import dotenv_values
from pathlib import Path
import requests


commands: dict = {
    0:  'SHIPMODE',  # Fully power down device, clears engine data information and makes detection process start again
    1:  'SETPARAMS 527=1;',  # For OBD
    11: 'FORCE SETPARAMS 527=1;',  # Forcing OBD
    2:  'SETPARAMS 527=2;',  # For J1939
    21: 'FORCE SETPARAMS 527=2;',  # Forcing J1939
    3:  'SETPARAMS 527=3;',  # For mixed 2 and 4
    31: 'FORCE SETPARAMS 527=3;',  # Forcing mixed 2 and 4
    4:  'SETPARAMS 527=4;',  # For J1708
    41: 'FORCE SETPARAMS 527=4;',  # Forcing J1708
    5:  'SETPARAMS 527=5;',  # For AutoDetect
    51: 'FORCE SETPARAMS 527=5;',  # Forcing AutoDetect
    6:  'SETPARAMS 527=6;',  # For Second J1939**
    61: 'FORCE SETPARAMS 527=6;',  # Forcing Second J1939**
    7:  'SETPARAMS 520=0;',  # Turning off silent mode
    8:  'DIAG CAN',          # Returns data on the device's CANBUS status
    81: 'DIAG ELD',          # Minimum conformity of found engine data for ELD usage
    82: 'DIAG DISC',         # Retrieves ECU data discovered
    83: 'DIAG NETWORK',      # Retrieves data on the device's network
    84: 'DIAG QUEUE',        # Returns information about the device's packet queue
    85: 'DIAG VERSION',      # Returns information on the device's version
    86: 'DIAG CONFIG',       # Retrieves information about the current configuration of a device
    87: 'DIAG DEVICEINFO',   # Retrieves information about the device BLE
    9:  'SETPARAMS 994=213403;',   # OBD odometer offset
    91: 'SETPARAMS 932=2;',      # Remove OBD EH override(use ELD EH)
    92: 'SETPARAMS 998=0;',      # Stops ELD device beeping
    93: 'SETPARAMS 542=1;',      # Potential fix for 65535 bluetooth firmware
    94: 'RESET O 39254000',      # Set desired ELD OD mult. by 1000
    95: 'RESET I 123456789',     # Set ELD EH mult by 3600
    10: 'RECAST',            # Pushing config on cast
    101: 'BLETEST 2',        # 87A, 88A, 87U, 88U - Resets bluetooth
    102: 'BLETEST 9',        # 87A, 88A, 87U, 88U - Reprogram bluetooth - only use if bluetooth reset is not working
    103: 'BLETEST 34',       # 87B, 88B - Resets bluetooth
    104: 'PURGECONFIG'        # 87B, 88B - Resets bluetooth
}


def open_skyonics_session(username: str, password: str, url: str, headers: dict) -> requests.session:
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    session: requests.session = requests.session()

    login = session.post(
        url=f"{url}/api/proxy/userlogin/login",
        data={'UserName': username, 'Password': password},
        headers=headers,
        verify=False
    )

    if login.status_code != 200:
        print(f"Login failed! Status code: {login.status_code}.")
        exit(1)

    return session


def close_skyonics_session(session: requests.session) -> None:
    session.close()


def send_command(session: requests.session, url: str, headers: dict, eld_serial_number: str, command: int) -> None:
    command_parameters: dict = {
        "DeviceSerialNumbers[]": eld_serial_number,
        "Command": commands.get(command),
        "CommandMode": 'UDPOnly',
        "WaitForPacket": 'true'
    }

    request = session.post(
        url=f"{url}/api/proxy/devicehealthoperations/sendcommanddevices",
        data=command_parameters,
        headers=headers,
        verify=False
    )

    if request.status_code != 200:
        print(f"Failed to send command! Status code: {request.status_code}.")
        exit(1)

    response: dict = request.json()

    print(f"""
        ELD S/N: {eld_serial_number}
        Command: {commands.get(command)}
        Success: {response.get("Success")}
        ETA: {(datetime.now() + timedelta(minutes=2)).strftime('%H:%M:%S')}
    """)


def main() -> None:
    base_dir: Path = Path(__file__).resolve().parent.parent

    env: dict = dotenv_values(dotenv_path=Path(base_dir, ".env"))

    username: str = env.get("lion8_skyonics_username")
    password: str = env.get("lion8_skyonics_password")
    url: str = env.get("skyonics_url")
    headers: dict = {"content-type": "application/x-www-form-urlencoded"}

    eld_serial_number: str = "87A030150048"
    command: int = 8

    lion8_session: requests.session = open_skyonics_session(
        username=username,
        password=password,
        url=url,
        headers=headers
    )

    send_command(
        session=lion8_session,
        url=url,
        headers=headers,
        eld_serial_number=eld_serial_number,
        command=command
    )

    close_skyonics_session(session=lion8_session)


if __name__ == "__main__":
    main()
