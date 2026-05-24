from pza.prints import (
    print_error,
    print_footer,
    print_header,
    print_label,
    print_line,
    print_separator,
    print_subheader,
    print_with_label,
)
from pza.pie import AppHub
import pza.pie
import pza.database

from pathlib import Path

def resolve_output_file_path(CurrentHub: AppHub, output_file_path: Path, force: bool) -> Path:
    """
    Handles file existence conflicts.
    If force is True, overwrites without prompt.
    """
    if force or not output_file_path.exists():
        return output_file_path
    CurrentHub.logger.info(f"The output file '{output_file_path.name}' already exists")
    choice = input(f"\nWould you like to overwrite or rename the existing file? [o/r]: ").lower()
    if choice == "o":
        CurrentHub.logger.info(f"Overwriting: {output_file_path.name}")
    else:
        if choice != "r":
            CurrentHub.logger.warning(f"Falling back to rename due to invalid response '{choice}'")
        counter = 1
        stem = output_file_path.stem
        suffix = output_file_path.suffix
        while output_file_path.exists():
            output_file_path = output_file_path.with_name(f"{stem}_{counter}{suffix}")
            counter += 1
        CurrentHub.logger.info(f"Renaming: {output_file_path.name}")
    return output_file_path

def save_recent_file(CurrentHub: AppHub, file_path: str) -> bool:
    """
    Inserts the file path into the RecentFiles database table.
    """
    conn = CurrentHub.database.connect()
    if not conn:
        CurrentHub.logger.warning(f"Error saving recent file: Database connection error")
        return False
    sql = f"""
        INSERT INTO History (input_file, timestamp)
        VALUES (?, DATETIME('now'))
    """
    parameters = (file_path,)
    executed = pza.database.sql_execute(sql, parameters, conn)
    if not executed:
        CurrentHub.logger.warning(f"Error saving recent file: Database execute error")
        conn.close()
        return False
    CurrentHub.logger.warning(f"Recent file saved")
    conn.close()
    return True

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()