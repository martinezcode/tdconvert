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
        CurrentHub.logger.info(f"Unable to launch app")
        return

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
    input_file_path = Path(input)

    # 1. Validation
    if not input_file_path.exists():
        CurrentHub.logger.error(f"Input file not found: {input_file_path}")
        return

    if input_file_path.suffix.lower() not in [".md", ".docx"]:
        CurrentHub.logger.error(f"Unsupported file format: {input_file_path.suffix}")
        return

    # 2. Determine Output Path
    if not output:
        CurrentHub.logger.info(f"Using automatic output file path")
        new_suffix = ".docx" if input_file_path.suffix.lower() == ".md" else ".md"
        output_file_path = input_file_path.with_suffix(new_suffix)
    else:
        CurrentHub.logger.info(f"Using provided output file path")
        output_file_path = Path(output)

    # 3. Conflict Handling
    output_file_path = library.handle_output_conflict(CurrentHub, output_file_path, force)

    # 4. Conversion Logic
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

        library.save_to_history(CurrentHub, str(input_file_path))

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
    pass

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()
