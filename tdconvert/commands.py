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

# --- Primary app entry point ---
# --- Runs when app is launched by name ---

def welcome(CurrentHub: AppHub) -> None:
    """
    The main interface entry point.
    This is the default mode if no command is given.
    """
    CurrentHub.logger.info(f"Welcome to {CurrentHub.display_name} version {CurrentHub.version}")

    database_populated = library.populate_database_formats(CurrentHub)
    if database_populated:
        CurrentHub.logger.info(f"Ready for data")
    else:
        CurrentHub.logger.info(f"So sorry for the error")
        # Close the app

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
    format: str = "",
    force: bool = False,
    dry: bool = False
) -> None:
    """
    Convert between MS Word docx and markdown md.
    Auto-detects file type from extension.
    Use `format` to override extension mapping with provided format.
    Use `output` to override automatic file naming or output folder.
    Use `force` to override existing file conflict option.
    Use `dry` to dry run conversion path without creating output files.
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
        return

    # Populate format data
    database_populated = library.populate_database_formats(CurrentHub)
    if not database_populated:
        CurrentHub.logger.error(f"{CurrentHub.display_name} is unable to continue without required database records")
        return

    CurrentHub.logger.info(f"Ready for data")

    # Validate the input file
    if not input:
        CurrentHub.logger.error(f"No input file provided")
        return

    input_file_path = Path(input)

    if not input_file_path.exists():
        if dry:
            CurrentHub.logger.warning(f"Input file not found: {input_file_path}")
            CurrentHub.logger.warning(f"Proceeding with dry run")
        else:
            CurrentHub.logger.error(f"Input file not found: {input_file_path}")
            return

    CurrentHub.logger.info(f"Ready to convert: {input_file_path}")

    # Identify input format from extension
    if format:
        format_id = format
        CurrentHub.logger.info(f"Using provided format: {format_id}")
    else:
        extension_id = input_file_path.suffix.lower()
        format_id = library.get_format_by_extension(CurrentHub, extension_id)
        if not format_id:
            CurrentHub.logger.error(f"Format unavailable")
            return
        CurrentHub.logger.info(f"Found format for {extension_id}: {format_id}")

    # Get mapping for profile and input format
    mapping = library.get_mapping_by_keys(CurrentHub, CurrentHub.profile, format_id)

    if not mapping:
        CurrentHub.logger.error(f"Mapping unavailable")
        CurrentHub.logger.error(f"Run `tdconvert load --json` to import a mapping")
        return

    for key, value in mapping.items():
        CurrentHub.logger.debug(f"{key}: {value}")

    engine_id = mapping.get("engine_id", None)
    output_format_ids = mapping.get("output_format_ids", [])
    output_engine_ids = mapping.get("output_engine_ids", [])
    output_extension_ids = mapping.get("output_extension_ids", [])
    conflict_option = mapping.get("engine_id", "prompt")

    if not engine_id or \
        len(output_format_ids) != len(output_engine_ids) or \
        len(output_format_ids) != len(output_extension_ids) or \
        not conflict_option:
        CurrentHub.logger.error(f"Mapping invalid")
        return

    # Determine output paths
    if output:
        CurrentHub.logger.error(f"todo: Use `output` override output file paths")
        return
    else:
        CurrentHub.logger.info(f"Using automatic output file path")
        output_file_paths = []

        for output_extension_id in output_extension_ids:
            output_file_path = input_file_path.with_suffix(output_extension_id)
            CurrentHub.logger.debug(f"Path {output_file_path}")
            output_file_paths.append(output_file_path)

    CurrentHub.logger.info(f"Ready to output {len(output_file_paths)} files")

    for output_file_path in output_file_paths:
        # Conflict Handling
        output_file_path = library.resolve_output_file_path(CurrentHub, output_file_path, force)
        CurrentHub.logger.info(f"Ready to output: {output_file_path}")

        # Execute conversion
        CurrentHub.logger.info(f"Converting: {input_file_path} -> {output_file_path}")

        try:
            match format_id:
                case "markdown":
                    CurrentHub.logger.debug(f"Using {engine_id} engine for: {format_id}")

                    # Use alternate Pandoc format for specified markdown style
                    if engine_id == "pandoc":
                        markdown_format = format_id # markdown
                    else:
                        markdown_format = engine_id # markdown_strict, gfm
                    CurrentHub.logger.debug(f"Markdown Format: {markdown_format}")

                    if dry:
                        CurrentHub.logger.info(f"Successfully completed dry run for: {output_file_path}")
                    else:
                        pypandoc.convert_file(
                            source_file=str(input_file_path),
                            to=output_format_ids.pop(0),
                            format=markdown_format,
                            outputfile=str(output_file_path)
                        )
                        CurrentHub.logger.info(f"Successfully converted to: {output_file_path}")
                case _:
                    if dry:
                        CurrentHub.logger.info(f"Successfully completed dry run for: {output_file_path}")
                    else:
                        pypandoc.convert_file(
                            source_file=str(input_file_path),
                            to=output_format_ids.pop(0),
                            format=format_id,
                            outputfile=str(output_file_path)
                        )
                        CurrentHub.logger.info(f"Successfully converted to: {output_file_path}")
        except Exception as e:
            CurrentHub.logger.error(f"Conversion failed: {e}")
            return

    # Save to history
    library.save_recent_file(CurrentHub, str(input_file_path))
    return

# --- Load entry point ---
# --- Runs when app is launched with command 'load' ---

def load(
    CurrentHub: AppHub,
    json: str = ""
) -> None:
    """
    Import mappings from a JSON file.
    """
    # Validate the hub
    if not CurrentHub:
        CurrentHub.logger.error(f"Unable to launch app")
        return

    # Perform onboarding if onboarding_required flag is True in settings
    if not CurrentHub.setup():
        # Required onboarding failed or user quit
        CurrentHub.logger.error(f"{CurrentHub.display_name} is unable to continue without required onboarding")
        return

    # Populate format data
    database_populated = library.populate_database_formats(CurrentHub)
    if not database_populated:
        CurrentHub.logger.error(f"{CurrentHub.display_name} is unable to continue without required database records")
        return

    CurrentHub.logger.info(f"Ready for data")

    # Validate the input file
    if not json:
        CurrentHub.logger.error(f"No JSON file provided")
        return

    json_file_path = Path(json)

    if not json_file_path.exists():
        CurrentHub.logger.error(f"JSON file not found: {json_file_path}")
        return

    mappings = pza.pie.read_json_file_to_dictionary(json) # Actually returns list or dict

    if not mappings:
        CurrentHub.logger.error(f"Invalid JSON file: {json_file_path}")
        return

    if type(mappings) == dict:
        mapping_saved = library.upsert_mapping(
            CurrentHub,
            mappings.get("profile_id", CurrentHub.profile),
            mappings.get("format_id", None),
            mappings.get("engine_id", None),
            mappings.get("output_format_ids", []),
            mappings.get("output_engine_ids", []),
            mappings.get("conflict_option", "prompt")
        )
        if mapping_saved:
            CurrentHub.logger.info(f"Imported mapping:\n{mappings}")
        else:
            CurrentHub.logger.error(f"Unable to import:\n{mappings}")
            return
    elif type(mappings) == list:
        for mapping in mappings:
            if type(mapping) != dict:
                CurrentHub.logger.warning("Unable to import invalid mapping:\n{mapping}")
                continue
            mapping_saved = library.upsert_mapping(
                CurrentHub,
                mapping.get("profile_id", CurrentHub.profile),
                mapping.get("format_id", None),
                mapping.get("engine_id", None),
                mapping.get("output_format_ids", []),
                mapping.get("output_engine_ids", []),
                mapping.get("conflict_option", "prompt")
            )
            if mapping_saved:
                CurrentHub.logger.info(f"Imported mapping:\n{mapping}")
            else:
                CurrentHub.logger.warning(f"Unable to import:\n{mapping}")
                continue
    else:
        CurrentHub.logger.error(f"Invalid JSON file type: {json_file_path}")
        return

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
        CurrentHub.logger.error(f"Unable to initialize")
        return

    # Make sure database is available
    if not CurrentHub.database.database_created:
        CurrentHub.logger.error(f"The database is unavailable")
        return

    # Connect to database
    conn = CurrentHub.database.connect()
    if not conn:
        CurrentHub.logger.error(f"Database connection failed")
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

# --- Mapping entry point ---
# --- Runs when app is launched with command 'map' ---
# --- May also be called from `convert` if file is an umapped format ---

def map(
    CurrentHub: AppHub,
    format_id: str = "",
) -> bool:
    """
    File format mapping CRUD.
    Each readable format can be mapped to one or more writeable formats.
    Use `format_id` argument for standalone add/edit of a readable format mapping.
    """
    pass

    # Begin CRUD mode Loop

        # If format_id was provided

            # If format_id does not match a valid readable format, return False, else advance to Action 1

        # Else

            # Display table of mapped readable formats and list or grid of available unmapped formats

            # Prompt with 3 possible actions

            # User should be able to specify a format to add/edit and initiate Action 1 from this prompt

            # User should be able to specify one or more formats to delete and initiate Action 2 from this prompt

            # User should be able to initiate Action 3 from this prompt

        # Action 1: Add or edit a readable format mapping

            # Prompt with mapping criteria

            # User can choose one or more writable formats to assign to the chosen readable format

            # User can choose an option for handling existing output files (overwrite, rename, prompt)

            # User can choose an engine or keep default engine (disabled if only one engine is available)

            # Delete existing mapping if one exists (clean up junction tables)

            # Add the new mapping

            # If format_id was provided

                # Return to caller

                # If mapping was saved, return True, else return False

            # Else

                # Track change made

                # Continue CRUD mode loop (return to main prompt)

        # Action 2: Delete one or more readable format mappings

            # Prompt for confirmation of deletion

            # If confirmed, delete mapping from database

            # Track change made

            # Continue CRUD mode loop (return to main prompt)

        # Action 3: Quit

            # Display current state and summary of changes made

            # Exit CRUD mode loop to quit the app

    # return True


if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()
