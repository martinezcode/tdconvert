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
import pza.settings
import pza.database

from tdconvert import library

from pathlib import Path
import pypandoc
import os

# --- Primary app entry point ---
# --- Runs when app is launched by name ---

def welcome(CurrentHub: AppHub) -> None:
    """
    The main interface entry point.
    This is the default mode if no command is given.
    """
    CurrentHub.logger.info(f"Welcome to {CurrentHub.display_name} version {CurrentHub.version}")
    CurrentHub.logger.info(f"Thank you for using {CurrentHub.display_name}")
    return

# --- Test entry point ---
# --- Runs when app is launched with command 'test' ---

def test(CurrentHub: AppHub) -> None:
    """
    Runs basic framework feature tests.
    """
    # Validate the hub
    if not CurrentHub:
        CurrentHub.logger.error(f"Unable to launch app")
        return

    # Perform onboarding if onboarding_required flag is True in settings
    if not CurrentHub.setup():
        # Required onboarding failed or user quit
        CurrentHub.logger.error(f"{CurrentHub.display_name} is unable to continue without required onboarding")

    # Introduce the app
    CurrentHub.logger.info(f"Welcome to {CurrentHub.display_name} version {CurrentHub.version}")
    CurrentHub.logger.info(f"Test Mode Activated")
    CurrentHub.logger.info(CurrentHub)
    CurrentHub.list()

    # Test Settings
    CurrentHub.logger.info(f"Testing Settings")
    settings = CurrentHub.settings.get_settings()
    pza.settings.list_settings(settings)

    # Test Database
    CurrentHub.logger.info(f"Testing Database")
    conn = CurrentHub.database.connect()
    CurrentHub.logger.info(f"Database connected" if conn else f"Unable to connect to database")

    # Close the app
    CurrentHub.logger.info(f"Thank you for using {CurrentHub.display_name} version {CurrentHub.version}")

    return

# --- Convert entry point ---
# --- Runs when app is launched with command 'convert' ---

def convert(
    CurrentHub: AppHub,
    input: str = "",
    output: str = "",
    force: bool = False
) -> None:
    """
    Convert between MS Word docx and markdown md.
    Auto-detects file type from extension.
    Uses original file name in same directory if no output path is provided.
    """
    # Validate the hub
    if not CurrentHub:
        CurrentHub.logger.error(f"Unable to launch app")
        return

    # Perform onboarding if onboarding_required flag is True in settings
    if not CurrentHub.setup():
        # Required onboarding failed or user quit
        CurrentHub.logger.error(f"{CurrentHub.display_name} is unable to continue without required onboarding")

    # Validate the input file
    if not input:
        CurrentHub.logger.error(f"No input file provided")
        return

    input_file_path = Path(input)

    if not input_file_path.exists():
        CurrentHub.logger.error(f"Input file not found: {input_file_path}")
        return

    if input_file_path.suffix.lower() not in [".md", ".docx"]:
        CurrentHub.logger.error(f"Unsupported file format: {input_file_path.suffix}")
        return

    # Determine Output Path
    if not output:
        CurrentHub.logger.info(f"Using automatic output file path")
        new_suffix = ".docx" if input_file_path.suffix.lower() == ".md" else ".md"
        output_file_path = input_file_path.with_suffix(new_suffix)
    else:
        CurrentHub.logger.info(f"Using provided output file path")
        output_file_path = Path(output)

    # Conflict Handling
    output_file_path = library.resolve_output_file_path(CurrentHub, output_file_path, force)

    # Conversion Logic
    try:
        CurrentHub.logger.info(f"Starting conversion: {input_file_path} -> {output_file_path}")

        # Determine target format for Pandoc
        # .md -> docx, .docx -> markdown
        target_format = 'docx' if input_file_path.suffix.lower() == '.md' else 'markdown'

        # Execute conversion
        pypandoc.convert_file(
            str(input_file_path),
            target_format,
            outputfile=str(output_file_path)
        )

        CurrentHub.logger.info(f"Successfully converted to: {output_file_path}")

        library.save_recent_file(CurrentHub, str(input_file_path))

    except Exception as e:
        CurrentHub.logger.error(f"Conversion failed: {e}")

# --- Recent Files entry point ---
# --- Runs when app is launched with command 'recent' ---

def recent(
    CurrentHub: AppHub,
    limit: int = 10
) -> None:
    """
    Displays numbered recent files stored in AppHub database.
    Prompts for choice of file number to reconvert.
    """
    # Validate the hub
    if not CurrentHub:
        CurrentHub.logger.error(f"Unable to launch app")
        return

    # Make sure database is available
    if not CurrentHub.database.database_created:
        CurrentHub.logger.error(f"The database is unavailable.")
        return

    conn = CurrentHub.database.connect()
    if not conn:
        CurrentHub.logger.error(f"Database unavailable")
        return

    # Build the query
    sql_limit = f"LIMIT {limit}"
    if not limit or limit <= 0:
        CurrentHub.logger.warning(f"Falling back to default limit due to invalid input: '{limit}'")
        sql_limit = "LIMIT 10"
    sql = f"""
        SELECT DISTINCT input_file
        FROM
            History
        ORDER BY timestamp desc
        {sql_limit}
    """
    parameters = None

    # Search the database
    file_rows = pza.database.sql_select(sql, parameters, conn)
    if not file_rows:
        CurrentHub.logger.info(f"No files found")
        conn.close()
        return None

    # Display all matches
    file_indexes = {}
    idx = 0
    for file_row in file_rows:
        idx += 1
        input_file = file_row["input_file"]
        print(f"{idx}. {input_file}")
        file_indexes[f"{idx}"] = input_file

    # Prompt for choice of conversion to run
    while True:
        response = input(f"\nEnter a number to run the conversion or type 'q' to quit:")
        if response.lower().startswith('q'):
            print("Goodbye")
            break
        else:
            input_file = file_indexes.get(response, None)
            if not input_file:
                print(f"Invalid file number: {response}")
                continue
            else:
                print(f"Converting: {input_file}\n")
                convert(CurrentHub, input_file)
                break

    conn.close()

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()
