import customtkinter
import requests
import urllib3
import json
import csv


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("450x500")
        self.title("AnyTrek GPSs for deactivation")

        self.button = customtkinter.CTkButton(self, text="Choose CSV file...", command=self.file_input)
        self.button.grid(row=0, column=0, padx=20, pady=20)

        self.error = customtkinter.CTkLabel(self, text="", fg_color="transparent")
        self.error.grid(row=0, column=2, padx=20, pady=20)

        self.label_for_number = customtkinter.CTkLabel(self, text="Number of devices:", fg_color="transparent")
        self.label_for_number.grid(row=2, column=0, padx=20, pady=20)

        self.number_of_devices = customtkinter.CTkTextbox(self, width=50, height=10)
        self.number_of_devices.configure(state="disabled")
        self.number_of_devices.grid(row=2, column=2, padx=20, pady=10)

        self.label_for_devices = customtkinter.CTkLabel(self, text="List of devices:", fg_color="transparent")
        self.label_for_devices.grid(row=4, column=0, padx=20, pady=20)

        self.devices = customtkinter.CTkTextbox(self, width=200, height=300)
        self.devices.configure(state="disabled")
        self.devices.grid(row=4, column=2, padx=20, pady=20)

    def file_input(self) -> None:
        file = customtkinter.filedialog.askopenfilename()
        if file.endswith(".csv"):
            self.number_of_devices.configure(state="normal")
            self.number_of_devices.delete(index1="0.0", index2="end")
            self.number_of_devices.configure(state="disabled")

            self.devices.configure(state="normal")
            self.devices.delete(index1="0.0", index2="end")
            self.devices.configure(state="disabled")

            anytrek: list[str] = []
            with open(file, "r") as f:
                reader = csv.DictReader(f)
                for line in reader:
                    sn: str = line.get("Device ID")[0:14]
                    if sn not in anytrek:
                        anytrek.append(sn)
            self.for_deactivation(anytrek_gpss=anytrek)
        else:
            self.error.configure(text="Not a CSV file!", fg_color="red")

    @staticmethod
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

    @staticmethod
    def close_session(session: requests.session, url: str) -> None:
        session.post(url=f"{url}/web/logout", verify=False)
        session.close()

    @staticmethod
    def get_gps_devices(session: requests.session, url: str) -> dict:
        endpoint: str = ("web/superAdmin/gpss?page=1&elements=9999&orderBy=serialNum&asc=true&status=active&"
                         "modelIds=d210%2Cd410%2Cd430%2Cgb130mg%2Cgl520mg%2Cgv620mg%2Cindash1508%2Cround1611%2C"
                         "oval1711%2Cthermo1802%2Cround2211%2CspireonTrailer%2CspireonTruck&manufacturer=anytrek&"
                         "showUnassigned=true&startTime=1546300800000&endTime=1893875200000&forceFinished=false&"
                         "eventTypes=") \
            if not url.split(".")[1] == "routemate" else \
            ("web/superAdmin/gpss?page=1&elements=25&orderBy=serialNum&asc=true&status=active%2Cdeactivated%2ConHold%2C"
             "replaced%2Cunassigned&modelIds=d210%2Cd410%2Cd430%2Cgb130mg%2Cgl520mg%2Cgv620mg%2Cindash1508%2C"
             "round1611%2Coval1711%2Cround2211%2Csint229l%2CspireonTrailer%2CspireonTruck&manufacturer=anytrek&"
             "showUnassigned=true&startTime=1546300800000&endTime=1738713600000&forceFinished=false&eventTypes=")

        devices: dict = session.get(
            url=f"{url}/{endpoint}").json()

        return devices

    def for_deactivation(self, anytrek_gpss: list[str]) -> None:
        self.error.configure(text="Working...", fg_color="transparent")

        base_urls: dict[str, str] = {
            "eldrider": "https://eldrider.com",
            "xeld": "https://cloud.xeld.us",
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

        our_gpss: list = []
        for platform, base_url in base_urls.items():
            session: requests.session = self.get_session(url=base_url, password="devanjamen")
            devices: dict = self.get_gps_devices(session=session, url=base_url).get("data")
            if devices:
                for gps in devices:
                    if gps.get("manufacturer") == "anytrek" and gps.get("status") == "active":
                        sn: str = gps.get("serialNum")[0:14]
                        if sn not in our_gpss:
                            our_gpss.append(sn)
                        continue
            self.close_session(session=session, url=base_url)

        result: list[str] = []
        for device in anytrek_gpss:
            if device not in our_gpss:
                result.append(device)

        self.number_of_devices.configure(state="normal")
        self.number_of_devices.insert(index="0.0", text=len(result))
        self.number_of_devices.configure(state="disabled")

        self.devices.configure(state="normal")
        self.devices.insert(index="0.0", text="\n".join(result))
        self.devices.configure(state="disabled")

        self.error.configure(text="Done", fg_color="transparent")


if __name__ == "__main__":
    app = App()

    app.mainloop()
