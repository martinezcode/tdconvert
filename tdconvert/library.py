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
import sqlite3

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

def populate_database_formats(CurrentHub: AppHub) -> bool:
    """
    Imports format data into the database.
    Adds new formats if they don't already exist.
    """
    # Connect to the database
    conn = CurrentHub.database.connect()
    if not conn:
        CurrentHub.logger.error("Unable to connect to database")
        return False

    CurrentHub.logger.info("Checking for database changes")

    # Get the formats
    formats = recipe.get_format_recipe()
    cursor = conn.cursor()

    try:
        # Import the readable formats
        conn.execute("BEGIN TRANSACTION")

        for format_id, details in formats.items():

            # Check if this format already exists in the Formats table
            sql = "SELECT format_id FROM Formats WHERE format_id = ?"
            # CurrentHub.logger.debug(f"\n\n{sql}\n")
            parameters = (format_id,)
            cursor.execute(sql, parameters)
            format_row = cursor.fetchone()

            if not format_row:
                CurrentHub.logger.debug(f"========== {format_id} (Adding)")

                # CurrentHub.logger.debug(f"\n==========\n{format_id}\n==========")
                # CurrentHub.logger.debug(f"details:\n\n{details}\n")

                # Insert new format
                sql = f"""
                    INSERT INTO Formats
                    (format_id, description, engine_description, engine_default, is_readable, is_writeable)
                    VALUES
                    (?, ?, ?, ?, ?, ?)
                """
                # CurrentHub.logger.debug(f"Formats: {format_id}\n\n{sql}\n")
                parameters = (
                    format_id,
                    details.get('description', 'none'),
                    details.get('engine_description', 'none'),
                    details.get('engine_default', 'none'),
                    details['is_readable'],
                    details['is_writeable'],
                )
                cursor.execute(sql, parameters)
            else:
                CurrentHub.logger.debug(f"========== {format_id} (Ready)")

            # Sync Extensions (check for existence before inserting)
            for extension_id in details.get('extensions', []):
                sql = "SELECT extension_id FROM Extensions WHERE extension_id = ?"
                # CurrentHub.logger.debug(f"\n\n{sql}\n")
                parameters = (extension_id,)
                cursor.execute(sql, parameters)
                extension_row = cursor.fetchone()
                if not extension_row:
                    sql = "INSERT INTO Extensions (extension_id) VALUES (?)"
                    # CurrentHub.logger.debug(f"Extensions: {extension_id}\n\n{sql}\n")
                    parameters = (extension_id,)
                    cursor.execute(sql, parameters)

                # Check link existence
                sql = "SELECT 1 FROM FormatExtensions WHERE format_id = ? AND extension_id = ?"
                # CurrentHub.logger.debug(f"\n\n{sql}\n")
                parameters = (format_id, extension_id)
                cursor.execute(sql, parameters)
                if not cursor.fetchone():
                    sql = "INSERT INTO FormatExtensions (format_id, extension_id) VALUES (?, ?)"
                    # CurrentHub.logger.debug(f"FormatExtensions: {extension_id}\n\n{sql}\n")
                    parameters = (format_id, extension_id)
                    cursor.execute(sql, parameters)

            # Sync Engines (check for existence before inserting)
            for engine_id in details.get('engines', []):
                sql = "SELECT engine_id FROM Engines WHERE engine_id = ?"
                # CurrentHub.logger.debug(f"\n\n{sql}\n")
                parameters = (engine_id,)
                cursor.execute(sql, parameters)
                engine_row = cursor.fetchone()
                if not engine_row:
                    sql = "INSERT INTO Engines (engine_id) VALUES (?)"
                    # CurrentHub.logger.debug(f"Engines: {engine_id}\n\n{sql}\n")
                    parameters = (engine_id,)
                    cursor.execute(sql, parameters)

                # Check link existence
                sql = "SELECT 1 FROM FormatEngines WHERE format_id = ? AND engine_id = ?"
                # CurrentHub.logger.debug(f"\n\n{sql}\n")
                parameters = (format_id, engine_id)
                cursor.execute(sql, parameters)
                if not cursor.fetchone():
                    sql = "INSERT INTO FormatEngines (format_id, engine_id) VALUES (?, ?)"
                    # CurrentHub.logger.debug(f"FormatEngines: {engine_id}\n\n{sql}\n")
                    parameters = (format_id, engine_id)
                    cursor.execute(sql, parameters)

            # CurrentHub.logger.debug(f"\nCommit")
            conn.commit()

    except Exception as e:
        conn.rollback()
        CurrentHub.logger.error(f"Database population failed: {e}")
        conn.close()
        return False

    # Close the database
    CurrentHub.logger.info("Database formats are ready")
    conn.close()
    return True

def populate_sample_data(CurrentHub: AppHub) -> bool:
    """
    Imports sample data into the database.
    Adds new records if they don't already exist.
    """
    # Connect to the database
    conn = CurrentHub.database.connect()
    if not conn:
        CurrentHub.logger.error("Unable to connect to database")
        return False

    CurrentHub.logger.info("Populating sample data")

    # Get the formats
    formats = recipe.get_format_recipe()

    try:
        # Import the lists
        conn.execute("BEGIN TRANSACTION")

        for format_id, details in formats.items():



            if not details["is_readable"]:
                CurrentHub.logger.debug(f"========== {format_id} (Output only)")
            else:
                mapping_exists = upsert_mapping(
                    CurrentHub,
                    CurrentHub.profile,
                    format_id,
                    details["test_engine"],
                    details["test_output_formats"],
                    details["test_output_engines"],
                    details["test_conflict_option"],
                    conn
                )
                if mapping_exists:
                    CurrentHub.logger.debug(f"========== {format_id} (Ready)")
                else:
                    CurrentHub.logger.debug(f"========== {format_id} (Failed)")

        conn.commit()

    except Exception as e:
        conn.rollback()
        CurrentHub.logger.error(f"Database population failed: {e}")
        conn.close()
        return False

    # Close the database
    CurrentHub.logger.info("Sample data is ready")
    conn.close()
    return True

def upsert_mapping(
    CurrentHub: AppHub,
    profile_id: str,
    format_id: str,
    engine_id: str,
    output_format_ids: list[str],
    output_engine_ids: list[str],
    conflict_option: str = "prompt",
    conn: sqlite3.Connection | None = None
) -> bool:
    """
    Add or replace a format mapping in the database.
    """
    # Manage connection lifecycle internally if not provided
    managed_conn = False
    if conn is None:
        conn = CurrentHub.database.connect()
        if not conn:
            CurrentHub.logger.error("Database unavailable")
            return False
        managed_conn = True

    if not format_id:
        CurrentHub.logger.error(f"No Format provided")
        return False

    try:
        if managed_conn:
            # Use full transaction if we are managing the conn
            conn.execute("BEGIN TRANSACTION")
        else:
            # Use a savepoint if a connection already exists
            conn.execute("SAVEPOINT upsert_mapping")

        cursor = conn.cursor()

        # Check for existing profile/format mapping
        cursor.execute(
            "SELECT format_map_id FROM FormatMap WHERE profile_id = ? AND format_id = ?",
            (profile_id, format_id)
        )
        row = cursor.fetchone()

        if row:
            # Delete mapping and clean up junction tables
            map_id = row[0]
            cursor.execute("DELETE FROM FormatMapOutputs WHERE format_map_id = ?", (map_id,))
            cursor.execute("DELETE FROM FormatMapEngines WHERE format_map_id = ?", (map_id,))
            cursor.execute("DELETE FROM FormatMap WHERE format_map_id = ?", (map_id,))

        # Insert the new mapping
        cursor.execute(
            "INSERT INTO FormatMap (profile_id, format_id, conflict_option) VALUES (?, ?, ?)",
            (profile_id, format_id, conflict_option)
        )
        map_id = cursor.lastrowid

        # Insert related input engine
        cursor.execute(
            "INSERT INTO FormatMapEngines (format_map_id, format_id, engine_id) VALUES (?, ?, ?)",
            (map_id, format_id, engine_id)
        )

        # Insert related output formats
        for output_format_id in output_format_ids:
            cursor.execute(
                "INSERT INTO FormatMapOutputs (format_map_id, format_id) VALUES (?, ?)",
                (map_id, output_format_id)
            )
            # Insert related output engine
            # Remove used engine from array so next iteration will grab the right one
            cursor.execute(
                "INSERT INTO FormatMapEngines (format_map_id, format_id, engine_id) VALUES (?, ?, ?)",
                (map_id, output_format_id, output_engine_ids.pop(0))
            )

        # Save the changes
        if managed_conn:
            conn.commit()
            conn.close()
        else:
            conn.execute("RELEASE SAVEPOINT upsert_mapping")

        return True

    except Exception as e:
        if managed_conn:
            conn.rollback()
            conn.close()
        else:
            conn.execute("ROLLBACK TO SAVEPOINT upsert_mapping")
        CurrentHub.logger.error(f"Upsert mapping failed: {e}")
        return False

def delete_mapping(
    CurrentHub: AppHub,
    format_map_id: int,
    conn: sqlite3.Connection | None = None
) -> bool:
    """
    Delete a mapping from the database.
    Deletes parent and related child records.
    """
    # Manage connection lifecycle internally if not provided
    managed_conn = False
    if conn is None:
        conn = CurrentHub.database.connect()
        if not conn:
            CurrentHub.logger.error("Database unavailable")
            return False
        managed_conn = True

    try:
        if managed_conn:
            # Use full transaction if we are managing the conn
            conn.execute("BEGIN TRANSACTION")
        else:
            # Use a savepoint if a connection already exists
            conn.execute("SAVEPOINT upsert_mapping")

        cursor = conn.cursor()

        # Delete related child records first to satisfy foreign key logic
        cursor.execute("DELETE FROM FormatMapOutputs WHERE format_map_id = ?", (format_map_id,))
        cursor.execute("DELETE FROM FormatMapEngines WHERE format_map_id = ?", (format_map_id,))

        # Delete the parent mapping
        cursor.execute("DELETE FROM FormatMap WHERE format_map_id = ?", (format_map_id,))

        deleted_count = cursor.rowcount

        # Save the changes
        if managed_conn:
            conn.commit()
            conn.close()
        else:
            conn.execute("RELEASE SAVEPOINT delete_mapping")

        return deleted_count > 0

    except Exception as e:
        if managed_conn:
            conn.rollback()
        else:
            conn.execute("ROLLBACK TO SAVEPOINT delete_mapping")
        CurrentHub.logger.error(f"Upsert mapping failed: {e}")
        conn.close()
        return False

def delete_mapping_by_keys(
    CurrentHub: AppHub,
    profile_id: str,
    format_id: str,
    conn: sqlite3.Connection | None = None
) -> bool:
    """
    Facade function to delete mapping via natural keys.
    """
    # Manage connection lifecycle internally if not provided
    managed_conn = False
    if conn is None:
        conn = CurrentHub.database.connect()
        if not conn:
            CurrentHub.logger.error(f"Database unavailable")
            return False
        managed_conn = True

    sql = f"SELECT format_map_id FROM FormatMap WHERE profile_id = ? AND format_id = ?"
    parameters = (profile_id, format_id)
    map_row = pza.database.sql_select_one(sql, parameters, conn)

    if map_row:
        mapping_deleted = delete_mapping(CurrentHub, map_row[0], conn)
    else:
        mapping_deleted = False
        CurrentHub.logger.warning(f"Unable to delete: {profile_id}/{format_id}")

    if managed_conn:
        conn.close()

    return mapping_deleted

def get_extension_by_format(
    CurrentHub: AppHub,
    format_id: str,
    conn: sqlite3.Connection | None = None
) -> str | None:
    """
    Lookup the default `extension_id` for the provided `format_id`.
    Defaults to first `extension_id` by row_id order.
    """
    # Manage connection lifecycle internally if not provided
    managed_conn = False
    if conn is None:
        conn = CurrentHub.database.connect()
        if not conn:
            CurrentHub.logger.error(f"Database unavailable")
            return False
        managed_conn = True

    sql = f"SELECT extension_id FROM FormatExtensions WHERE format_id = ? ORDER BY rowid LIMIT 1"
    parameters = (format_id,)
    extension_row = pza.database.sql_select_one(sql, parameters, conn)

    if not extension_row:
        CurrentHub.logger.error(f"Extension not found for: {format_id}")
        if managed_conn:
            conn.close()
        return None

    extension_id = extension_row[f"extension_id"]

    if managed_conn:
        conn.close()

    return extension_id

def get_format_by_extension(
    CurrentHub: AppHub,
    extension_id: str,
    conn: sqlite3.Connection | None = None
) -> str | None:
    """
    Lookup `format_id` for the provided `extension_id`.
    """
    # Manage connection lifecycle internally if not provided
    managed_conn = False
    if conn is None:
        conn = CurrentHub.database.connect()
        if not conn:
            CurrentHub.logger.error(f"Database unavailable")
            return False
        managed_conn = True

    sql = f"SELECT format_id FROM FormatExtensions WHERE extension_id = ?"
    parameters = (extension_id,)
    format_row = pza.database.sql_select_one(sql, parameters, conn)

    if not format_row:
        CurrentHub.logger.error(f"Format not found for: {extension_id}")
        if managed_conn:
            conn.close()
        return None

    format_id = format_row[f"format_id"]

    if managed_conn:
        conn.close()

    return format_id

def get_mapping_by_keys(
    CurrentHub: AppHub,
    profile_id: str,
    format_id: str,
    conn: sqlite3.Connection | None = None
) -> dict | None:
    """
    Lookup mapping details for the provided `profile_id` and `format_id`.
    """
    # Manage connection lifecycle internally if not provided
    managed_conn = False
    if conn is None:
        conn = CurrentHub.database.connect()
        if not conn:
            CurrentHub.logger.error(f"Database unavailable")
            return False
        managed_conn = True

    sql = f"SELECT * FROM FormatMap WHERE profile_id = ? and format_id = ?"
    parameters = (profile_id, format_id)
    format_map_row = pza.database.sql_select_one(sql, parameters, conn)

    if not format_map_row:
        CurrentHub.logger.error(f"Format mapping not found")
        if managed_conn:
            conn.close()
        return None

    format_map_id = format_map_row["format_map_id"]
    conflict_option = format_map_row["conflict_option"]

    engine_id = None
    output_format_ids = []
    output_engine_ids = []
    output_extension_ids = []

    sql = f"SELECT * FROM FormatMapOutputs WHERE format_map_id = ? ORDER BY rowid"
    parameters = (format_map_id,)
    output_format_rows = pza.database.sql_select(sql, parameters, conn)
    if not output_format_rows:
        CurrentHub.logger.error(f"No output formats")
        return None

    for row in output_format_rows:
        if row["format_id"] == format_id:
            CurrentHub.logger.error(f"Invalid output format: {row["format_id"]}")
            CurrentHub.logger.error(f"Output is the same as input: {format_id}")
            return None
        else:
            output_format_ids.append(row["format_id"])
            CurrentHub.logger.debug(f"Output Format: {row["format_id"]}")

            output_extension_id = get_extension_by_format(CurrentHub, row["format_id"], conn)
            if not output_extension_id:
                CurrentHub.logger.error(f"No output extension for: {format_id}")
                return

            output_extension_ids.append(output_extension_id)

    sql = f"SELECT * FROM FormatMapEngines WHERE format_map_id = ? ORDER BY rowid"
    parameters = (format_map_id,)
    engine_rows = pza.database.sql_select(sql, parameters, conn)
    if not engine_rows:
        CurrentHub.logger.error(f"No engines")
        return
    if len(engine_rows) != len(output_format_rows) + 1:
        CurrentHub.logger.error(f"Engine count mismatch")
        CurrentHub.logger.error(f"Number of engines ({engine_rows}) should match number of inputs and outputs ({len(output_format_rows) + 1})")
        return

    for row in engine_rows:
        if row["format_id"] == format_id:
            # Input engine
            engine_id = row["engine_id"]
            CurrentHub.logger.debug(f"Engine: {row["engine_id"]}")
        else:
            # Output engine
            output_engine_ids.append(row["engine_id"])
            CurrentHub.logger.debug(f"Output Engine: {row["engine_id"]}")
            CurrentHub.logger.debug(f"Output Extension: {output_extension_id}")

    mapping = recipe.get_mapping_recipe(
        profile_id,
        format_id,
        engine_id,
        output_format_ids,
        output_engine_ids,
        output_extension_ids,
        conflict_option
    )

    CurrentHub.logger.debug(f"Mapping found: {mapping}")

    if managed_conn:
        conn.close()

    return mapping


if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()