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

# --- Recipe definitions ---

def get_app_recipe(app_name: str, app_display_name: str, app_version: str) -> dict:
    """
    Defines app specifications.
    """
    recipe = {
        "name": app_name,
        "display_name": app_display_name,
        "version": app_version,
        "entry_point": "tdconvert.commands.welcome",
        "test_entry_point": "tdconvert.commands.test",
        "settings_recipe": get_settings_recipe(),
        "command_recipe": get_command_recipe(),
        "onboarding_recipe": get_onboarding_recipe(),
        "database_recipe": get_database_recipe(),
    }
    return recipe

def get_command_recipe() -> dict:
    """
    Defines command line interface commands and arguments.
    """
    recipe = {
        "convert": {
            "callback": "tdconvert.commands.convert",
            "help": "Convert an input file to one or more output files",
            "args": [
                {
                    "name": "--input",
                    "help": "Required input file path",
                    "action": None,
                    "exclusive": False,
                    "type": str,
                    "default": "",
                },
                {
                    "name": "--output",
                    "help": "Coming soon", # todo: Override output
                    "action": None,
                    "exclusive": False,
                    "type": str,
                    "default": "",
                },
                {
                    "name": "--format",
                    "help": "Override extension mapping to use a specific format",
                    "action": None,
                    "exclusive": False,
                    "type": str,
                    "default": "",
                },
                {
                    "name": "--force",
                    "help": "Automatically overwrite existing files",
                    "action": "store_true",
                    "exclusive": False,
                },
                {
                    "name": "--dry",
                    "help": "Dry run conversion path without creating output files",
                    "action": "store_true",
                    "exclusive": False,
                },
            ],
        },
        "recent": {
            "callback": "tdconvert.commands.recent",
            "help": "List recent files to reconvert",
            "args": [
                {
                    "name": "--limit",
                    "type": int,
                    "default": 10,
                    "help": "Optional number of files to list",
                    "action": None,
                    "exclusive": False,
                },
            ],
        },
        "load": {
            "callback": "tdconvert.commands.load",
            "help": "Import mappings from JSON file",
            "args": [
                {
                    "name": "--json",
                    "type": str,
                    "default": "",
                    "help": "JSON file to import",
                    "action": None,
                    "exclusive": True,
                },
            ],
        },
    }
    return recipe

def get_database_recipe() -> dict:
    """
    Defines app database schema.
    """
    recipe = {
        "schema_version": "0.4.2",
        "History": {
            "history_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "timestamp": "DATETIME",
            "profile_id": "TEXT",
            "format_id": "TEXT",
            "extension_id": "TEXT",
            "engine_id": "TEXT",
            "conflict_option": "TEXT",
            "output_format_ids": "TEXT",
            "output_engine_ids": "TEXT",
            "input_file": "TEXT",
            "output_files": "TEXT",
        },
        "Formats": {
            "format_id": "TEXT PRIMARY KEY",
            "description": "TEXT",
            "engine_description": "TEXT",
            "engine_default": "TEXT",
            "is_readable": "BOOLEAN",
            "is_writeable": "BOOLEAN",
        },
        "Extensions": {
            "extension_id": "TEXT PRIMARY KEY",
        },
        "Engines": {
            "engine_id": "TEXT PRIMARY KEY",
        },
        "FormatExtensions": {
            "format_id": "TEXT",
            "extension_id": "TEXT",
        },
        "FormatEngines": {
            "format_id": "TEXT",
            "engine_id": "TEXT",
        },
        "FormatMap": {
            "format_map_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "profile_id": "TEXT",
            "format_id": "TEXT",
            "conflict_option": "TEXT",
        },
        "FormatMapOutputs": {
            "format_map_id": "INTEGER",
            "format_id": "TEXT",
        },
        "FormatMapEngines": {
            "format_map_id": "INTEGER",
            "format_id": "TEXT",
            "engine_id": "TEXT",
        },
    }
    return recipe

def get_mapping_recipe(
    profile_id: str,
    format_id: str,
    engine_id: str,
    output_format_ids: list[str],
    output_engine_ids: list[str],
    output_extension_ids: list[str],
    conflict_option: str = "prompt",
) -> dict:
    mapping = {
        "profile_id": profile_id,
        "format_id": format_id,
        "engine_id": engine_id,
        "output_format_ids": output_format_ids,
        "output_engine_ids": output_engine_ids,
        "output_extension_ids": output_extension_ids,
        "conflict_option": conflict_option,
    }
    return mapping

def get_format_recipe() -> dict:
    """
    Defines supported conversion formats.
    Extensions must be unique to a format.
    Multiple formats cannot use the same extensions.
    Run with `convert --format` to override an extension mapping.
    """
    formats = {
        "markdown": {
            "extensions": [".md",".markdown"],
            "description": "Markdown",
            "is_readable": True,
            "is_writeable": True,
            "engine_description": "Markdown Style (Original, Pandoc Enhanced, or GitHub-Flavored)",
            "engine_default": "pandoc",
            "engines": [
                "markdown_strict",
                "pandoc",
                "gfm",
            ],
            "test_extension": ".md",
            "test_engine": "gfm",
            "test_conflict_option": "overwrite",
            "test_output_formats": ["docx", "html"],
            "test_output_engines": ["pandoc", "pandoc"],
            "test_file": "test.md",
            "test_output_files": ["test.docx", "test.html"],
        },
        "docx": {
            "extensions": [".docx",],
            "description": "Microsoft Word",
            "is_readable": True,
            "is_writeable": True,
            "engine_description": "Pandoc Conversion",
            "engine_default": "pandoc",
            "engines": [
                "pandoc",
            ],
            "test_extension": ".docx",
            "test_engine": "pandoc",
            "test_conflict_option": "overwrite",
            "test_output_formats": ["docx", "html"],
            "test_output_engines": ["pandoc", "pandoc"],
            "test_file": "test.docx",
            "test_output_files": ["test.docx", "test.html"],
        },
        "json": {
            "extensions": [".json",],
            "description": "JavaScript Object Notation",
            "is_readable": True,
            "is_writeable": True,
            "engine_description": "Pandoc Conversion",
            "engine_default": "pandoc",
            "engines": [
                "pandoc",
            ],
            "test_extension": ".json",
            "test_engine": "pandoc",
            "test_conflict_option": "overwrite",
            "test_output_formats": ["docx", "html"],
            "test_output_engines": ["pandoc", "pandoc"],
            "test_file": "test.json",
            "test_output_files": ["test.docx", "test.html"],
        },
        "rtf": {
            "extensions": [".rtf",],
            "description": "Rich Text Format",
            "is_readable": True,
            "is_writeable": True,
            "engine_description": "Pandoc Conversion",
            "engine_default": "pandoc",
            "engines": [
                "pandoc",
            ],
            "test_extension": ".rtf",
            "test_engine": "pandoc",
            "test_conflict_option": "overwrite",
            "test_output_formats": ["docx", "html"],
            "test_output_engines": ["pandoc", "pandoc"],
            "test_file": "test.rtf",
            "test_output_files": ["test.docx", "test.html"],
        },
        # "pdf": {
        #     "extensions": [".pdf",],
        #     "description": "Portable Document Format",
        #     "is_readable": False,
        #     "is_writeable": True,
        #     "engine_description": "PDF Output Engine",
        #     "engine_default": "pdflatex",
        #     "engines": [
        #         "pdflatex",
        #         "lualatex",
        #         "xelatex",
        #         "latexmk",
        #         "tectonic",
        #         "wkhtmltopdf",
        #         "weasyprint",
        #         "pagedjs-cli",
        #         "prince",
        #         "context",
        #         "groff",
        #         "pdfroff",
        #         "typst",
        #     ],
        #     "test_extension": None,
        #     "test_engine": None,
        #     "test_conflict_option": None,
        #     "test_output_formats": None,
        #     "test_output_engines": None,
        #     "test_file": None,
        #     "test_output_files": None,
        # },
        "csv": {
            "extensions": [".csv",],
            "description": "Comma Separated Values",
            "is_readable": True,
            "is_writeable": False,
            "engine_description": "Pandoc Conversion",
            "engine_default": "pandoc",
            "engines": [
                "pandoc",
            ],
            "test_extension": ".csv",
            "test_engine": "pandoc",
            "test_conflict_option": "overwrite",
            "test_output_formats": ["docx", "html"],
            "test_output_engines": ["pandoc", "pandoc"],
            "test_file": "test.csv",
            "test_output_files": ["test.docx", "test.html"],
        },
        "html": {
            "extensions": [".html",],
            "description": "HyperText Markup Language",
            "is_readable": True,
            "is_writeable": True,
            "engine_description": "Pandoc Conversion",
            "engine_default": "pandoc",
            "engines": [
                "pandoc",
            ],
            "test_extension": ".html",
            "test_engine": "pandoc",
            "test_conflict_option": "overwrite",
            "test_output_formats": ["docx", "html"],
            "test_output_engines": ["pandoc", "pandoc"],
            "test_file": "test.html",
            "test_output_files": ["test.docx", "test.html"],
        },
        "plain": {
            "extensions": [".txt",],
            "description": "Plain Text",
            "is_readable": False,
            "is_writeable": True,
            "engine_description": "Pandoc Conversion",
            "engine_default": "pandoc",
            "engines": [
                "pandoc",
            ],
            "test_extension": None,
            "test_engine": None,
            "test_conflict_option": None,
            "test_output_formats": None,
            "test_output_engines": None,
            "test_file": None,
            "test_output_files": None,
        },
    }
    return formats

def get_settings_recipe() -> dict:
    """
    Defines app default setting specifications.
    """
    recipe = {
        "onboarding_required": False, # Override framwork default
        "log_level": "debug",
    }
    return recipe

def get_onboarding_recipe() -> dict:
    """
    Defines app setup wizard specifications.
    """
    recipe = None
    return recipe

# --- Onboarding validation functions ---

# --- PLACEHOLDER ---

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()
