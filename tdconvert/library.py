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

def handle_output_conflict(CurrentHub: AppHub, output_file_path: Path, force: bool) -> Path:
    """
    Handles file existence conflicts.
    If force is True, overwrites without prompt.
    """
    if not output_file_path.exists() or force:
        return output_file_path

    CurrentHub.logger.info(f"\nConflict: The file '{output_file_path.name}' already exists.")
    choice = input("Would you like to (o)verwrite or (a)ppend a unique number? [o/a]: ").lower()

    if choice == 'a':
        counter = 1
        stem = output_file_path.stem
        suffix = output_file_path.suffix
        while output_file_path.exists():
            output_file_path = output_file_path.with_name(f"{stem}_{counter}{suffix}")
            counter += 1
        CurrentHub.logger.info(f"Saving as: {output_file_path.name}")
    else:
        CurrentHub.logger.info(f"Overwriting: {output_file_path.name}")

    return output_file_path

def save_to_history(CurrentHub: AppHub, file_path: str):
    """
    Inserts the file path into the RecentFiles database table.
    """
    pass
    # conn = CurrentHub.database.connect()
    # cursor = conn.cursor()
    # cursor.execute(
    #     "INSERT INTO RecentFiles (file_path, timestamp) VALUES (?, DATETIME('now'))",
    #     (file_path,)
    # )
    # conn.commit()
    # conn.close()

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()