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

from tdconvert import recipe

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

def populate_database_formats(CurrentHub) -> bool:
    """
    Imports format data into the database.
    Adds new formats if they don't already exist.
    """
    # Connect to the database
    conn = CurrentHub.database.connect()
    if not conn:
        CurrentHub.logger.error("Unable to connect to database")
        return False

    # Get the formats
    formats = recipe.get_format_recipe()
    cursor = conn.cursor()

    try:
        # Import the lists
        conn.execute("BEGIN TRANSACTION")

        for name, details in formats.items():
            # Check if this format already exists in the Formats table
            sql = "SELECT format_id FROM Formats WHERE format = ?"
            parameters = (name,)
            cursor.execute(sql, parameters)
            format_row = cursor.fetchone()

            if format_row:
                format_id = format_row[0]
            else:
                # Insert new format
                sql = f"""
                    INSERT INTO Formats
                        (format, description, readable, writeable, engine_description)
                    VALUES
                        (?, ?, ?, ?, ?)
                """
                parameters = (
                    name,
                    details.get('description', ''),
                    details.get('readable', False),
                    details.get('writeable', False),
                    details.get('engine_description', ''),
                )
                cursor.execute(sql, parameters)
                format_id = cursor.lastrowid

            # Sync Extensions (check for existence before inserting)
            for extension in details.get('extensions', []):
                sql = "SELECT extension_id FROM Extensions WHERE extension = ?"
                parameters = (extension,)
                cursor.execute(sql, parameters)
                extension_row = cursor.fetchone()
                if extension_row:
                    extension_id = extension_row[0]
                else:
                    sql = "INSERT INTO Extensions (extension) VALUES (?)"
                    parameters = (extension,)
                    cursor.execute(sql, parameters)
                    extension_id = cursor.lastrowid

                # Check link existence
                sql = "SELECT 1 FROM FormatExtensions WHERE format_id = ? AND extension_id = ?"
                parameters = (format_id, extension_id)
                cursor.execute(sql, parameters)
                if not cursor.fetchone():
                    sql = "INSERT INTO FormatExtensions (format_id, extension_id) VALUES (?, ?)"
                    parameters = (format_id, extension_id)
                    cursor.execute(sql, parameters)

            # Sync Engines (check for existence before inserting)
            for engine in details.get('engines', []):
                sql = "SELECT engine_id FROM Engines WHERE engine = ?"
                parameters = (engine,)
                cursor.execute(sql, parameters)
                engine_row = cursor.fetchone()
                if engine_row:
                    engine_id = engine_row[0]
                else:
                    sql = "INSERT INTO Engines (engine) VALUES (?)"
                    parameters = (engine,)
                    cursor.execute(sql, parameters)
                    engine_id = cursor.lastrowid

                # Check link existence
                sql = "SELECT 1 FROM FormatEngines WHERE format_id = ? AND engine_id = ?"
                parameters = (format_id, engine_id)
                cursor.execute(sql, parameters)
                if not cursor.fetchone():
                    sql = "INSERT INTO FormatEngines (format_id, engine_id) VALUES (?, ?)"
                    parameters = (format_id, engine_id)
                    cursor.execute(sql, parameters)

        conn.commit()

    except Exception as e:
        conn.rollback()
        CurrentHub.logger.error(f"Database population failed: {e}")
        conn.close()
        return False

    # Close the database
    conn.close()
    return True

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()