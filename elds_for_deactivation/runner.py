import os
import pandas as pd
from pathlib import Path


def list_directory_contents(directory: Path) -> list[Path]:
    return [Path(file) for file in os.listdir(directory) if file.endswith(".csv")]


def make_dataframe_from_csv(csv_file: Path) -> pd.DataFrame:
    return pd.read_csv(csv_file)


def merge_dataframes() -> pd.DataFrame:
    elds_directory: Path = Path("./elds/")
    files: list[Path] = list_directory_contents(directory=elds_directory)

    merged_dataframes: pd.DataFrame = pd.DataFrame(
        columns=["companyName", "dotNum", "companyStatus", "eldSerialNum", "eldStatus", "platform"]
    )

    for file in files:
        file_path = Path(elds_directory, file)
        merged_dataframes = pd.concat(
            [merged_dataframes, make_dataframe_from_csv(csv_file=file_path)]
        )

    return merged_dataframes


def filter_dataframe(df: pd.DataFrame, to_find: list[str], index_column: str) -> pd.DataFrame:
    columns = df.columns
    filtered_dataframe: pd.DataFrame = pd.DataFrame(
        columns=columns
    )

    df: pd.DataFrame = df.set_index([index_column])

    for index in to_find:
        to_concat: pd.DataFrame | pd.Series = df.loc[index]

        if type(to_concat) is pd.Series:
            tmp: pd.DataFrame = pd.DataFrame(
                columns=columns,
                index=[to_concat.name]
            )

            for column in columns:
                tmp[column] = to_concat.get(column)

            to_concat = tmp

        filtered_dataframe = pd.concat([filtered_dataframe, to_concat])
        filtered_dataframe.loc[index, "eldSerialNum"] = index

    return filtered_dataframe


def dataframe_to_xlsx(df: pd.DataFrame, path: Path, index_column: str) -> None:
    df.set_index([index_column]).to_excel(excel_writer=path)


def is_for_deactivation(eld: pd.DataFrame) -> bool:
    for_check: str | pd.DataFrame = eld.get("eldStatus")

    if type(for_check) is str:
        return True if for_check == "DEACTIVATED" else False

    tmp: list = list(set(for_check.tolist()))
    if len(tmp) == 1:
        return True if tmp[0] == "DEACTIVATED" else False

    return False


def main() -> None:
    elds: pd.DataFrame = merge_dataframes()

    shortened_elds: pd.DataFrame = (elds[["eldSerialNum", "eldStatus", "platform"]]
                                    .set_index(["eldSerialNum"])
                                    .sort_index())

    for_deactivation: list[str] = []

    indexes: set[str] = set(shortened_elds.index)
    for index in indexes:
        eld: pd.DataFrame = shortened_elds.loc[index]
        if is_for_deactivation(eld=eld):
            for_deactivation.append(index)

    result: pd.DataFrame = filter_dataframe(
        df=elds,
        to_find=for_deactivation,
        index_column="eldSerialNum"
    )

    dataframe_to_xlsx(
        df=result,
        path=Path("for_deactivation.xlsx"),
        index_column="eldSerialNum"
    )


if __name__ == "__main__":
    main()
