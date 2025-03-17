from cloudflare import get_scheduled_maintenances
from cloudflare import get_incidents

import sqlite3


def get_formatted_time(cf_time: str) -> str:
    return cf_time.split(".")[0].replace("T", " ") + " UTC"


def make_incident_message(name: str, created_at: str, link: str) -> str:
    return f"{name} - Incident recorded at {get_formatted_time(cf_time=created_at)}.\n Details: {link}"


def make_maintenance_message(name: str, scheduled_for: str, scheduled_until: str, link: str) -> str:
    return (f"{name} - Maintenance scheduled for {get_formatted_time(cf_time=scheduled_for)} until "
            f"{get_formatted_time(cf_time=scheduled_until)}.\n Details: {link}")

def execute_query(query: str, to_read: bool | None = False) -> list[sqlite3.Row] | None:
    connection = sqlite3.connect(database="events.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    result = None
    if to_read:
        result = cursor.execute(query).fetchall()
    else:
        cursor.execute(query)
        connection.commit()

    cursor.close()
    connection.close()

    return result


def create_events_table() -> None:
    """
    Creates "events" table if not exists with columns:
        source : str
            Source of event - "Cloudflare" or "DigitalOcean"
        event_ype : str
            Type of event - "incident" or "maintenance"
        event_status: str
            Status of event - "scheduled", "investigating"
        event_id : str
            ID of the event
        impact_level : str
            Impact level of the event - "maintenance", "minor", "major" or "critical"
        name : str
            Name of the event
        link : str
            Short link to more details about the event
        created_at : str
            Date of event creation
        scheduled_for : str
            Date and time when scheduled event begins
        scheduled_until : str
            Date and time when scheduled event ends
    """
    create_incidents_table: str = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            source VARCHAR(16),
            event_type VARCHAR(32),
            event_status VARCHAR(16),
            event_id VARCHAR(32) UNIQUE,
            impact VARCHAR(16),
            name VARCHAR(255),
            link VARCHAR(255),
            created_at VARCHAR(32),
            scheduled_for VARCHAR(32),
            scheduled_until VARCHAR(32)
        );
        """

    execute_query(query=create_incidents_table)


def main() -> None:
    create_events_table()

    db_events: list[sqlite3.Row] = execute_query(query="SELECT * FROM events;", to_read=True)
    db_event_ids: list[str] = [event["event_id"] for event in db_events]

    cf_scheduled_maintenances: list[dict] = get_scheduled_maintenances()
    cf_incidents: list[dict] = get_incidents()

    if cf_scheduled_maintenances:
        for event in cf_scheduled_maintenances:
            if event.get("id") not in db_event_ids:
                message = make_maintenance_message(
                    name=event.get("name"),
                    scheduled_for=event.get("scheduled_for"),
                    scheduled_until=event.get("scheduled_until"),
                    link=event.get("shortlink")
                )
                #
                #  TODO: slack webhook
                #
                query = f"""
                    INSERT INTO events(source, event_type, event_status, event_id, impact, name, link, created_at, scheduled_for, scheduled_until) VALUES
                    ('cloudflare', 'maintenance', '{event.get("status")}', '{event.get("id")}', '{event.get("impact")}', '{event.get("name")}', '{event.get("shortlink")}', '{event.get("created_at")}', '{event.get("scheduled_for")}', '{event.get("scheduled_until")}');
                """
                execute_query(query=query)

    if cf_incidents:
        for event in cf_incidents:
            if event.get("id") not in db_event_ids:
                message = make_incident_message(
                    name=event.get("name"),
                    created_at=event.get("created_at"),
                    link=event.get("shortlink")
                )
                #
                #  TODO: slack webhook
                #
                query = f"""
                    INSERT INTO events(source, event_type, event_status, event_id, impact, name, link, created_at, scheduled_for, scheduled_until) VALUES
                    ('cloudflare', 'incident', '{event.get("status")}', '{event.get("id")}', '{event.get("impact")}', '{event.get("name")}', '{event.get("shortlink")}', '{event.get("created_at")}', NULL, NULL);
                """
                execute_query(query=query)


if __name__ == "__main__":
    main()
