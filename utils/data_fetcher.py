from mysql.connector import connection


def fetch_data(query: str, params: dict, as_dict: bool = False) -> list[tuple] | list[dict]:
    db: str = params.get("database")
    host: str = params.get("host")
    user: str = params.get("user")
    password: str = params.get("password")

    con = connection.MySQLConnection(
        database=db,
        host=host,
        user=user,
        password=password,
        auth_plugin="mysql_native_password"
    )

    cursor = con.cursor(dictionary=True) if as_dict else con.cursor()

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    con.close()

    return result
