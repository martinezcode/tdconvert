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

def get_database_recipe() -> dict:
    """
    Defines app database schema.
    """
    recipe = {
        "schema_version": "0.4.2",
        "History": {
            "history_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "input_file": "TEXT",
            "output_files": "TEXT",
            "timestamp": "DATETIME",
        },
        "Extensions": {
            "extension_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "extension": "TEXT",
        },
        "Engines": {
            "engine_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "engine": "TEXT",
        },
        "Formats": {
            "format_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "format": "TEXT",
            "description": "TEXT",
            "readable": "BOOLEAN",
            "writeable": "BOOLEAN",
            "engine_description": "TEXT",
        },
        "FormatExtensions": {
            "format_id": "INTEGER",
            "extension_id": "INTEGER",
        },
        "FormatEngines": {
            "format_id": "INTEGER",
            "engine_id": "INTEGER",
        },
        "FormatMap": {
            "format_map_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "profile_id": "TEXT",
            "input_format_id": "INTEGER",
            "conflict_option": "TEXT",
        },
        "FormatMapOutputs": {
            "format_map_id": "INTEGER",
            "output_format_id": "INTEGER",
        },
    }
    return recipe

def get_format_recipe() -> dict:
    """
    Defines supported conversion formats.
    """
    formats = {
        "markdown": {
            "extensions": [".md",".markdown"],
            "description": "Markdown",
            "readable": True,
            "writeable": True,
            "engine_description": "Markdown Style (Original, Pandoc Enhanced, or GitHub-Flavored)",
            "engines": [
                "markdown_strict",
                "pandoc",
                "gfm",
            ]
        },
        "docx": {
            "extensions": [".docx",],
            "description": "Microsoft Word",
            "readable": True,
            "writeable": True,
        },
        "json": {
            "extensions": [".json",],
            "description": "JavaScript Object Notation",
            "readable": True,
            "writeable": True,
        },
        "rtf": {
            "extensions": [".rtf",],
            "description": "Rich Text Format",
            "readable": True,
            "writeable": True,
        },
        "pdf": {
            "extensions": [".pdf",],
            "description": "Portable Document Format",
            "readable": False,
            "writeable": True,
            "engine_description": "Engine for producing PDF Output",
            "engines": [
                "pdflatex",
                "lualatex",
                "xelatex",
                "latexmk",
                "tectonic",
                "wkhtmltopdf",
                "weasyprint",
                "pagedjs-cli",
                "prince",
                "context",
                "groff",
                "pdfroff",
                "typst",
            ]
        },
        "csv": {
            "extensions": [".csv",],
            "description": "Comma Separated Values",
            "readable": True,
            "writeable": False,
        },
        "html": {
            "extensions": [".html",],
            "description": "HyperText Markup Language",
            "readable": True,
            "writeable": True,
        },
        "plain": {
            "extensions": [".txt",],
            "description": "Plain Text",
            "readable": False,
            "writeable": True,
        },
    }
    return formats

def get_command_recipe() -> dict:
    """
    Defines command line interface commands and arguments.
    """
    recipe = {
        "convert": {
            "callback": "tdconvert.commands.convert",
            "help": "Convert docx to md or md to docx",
            "args": [
                {
                    "name": "--input",
                    "type": str,
                    "default": "",
                    "help": "Required input file path",
                    "action": None,
                    "exclusive": False,
                },
                {
                    "name": "--output",
                    "type": str,
                    "default": "",
                    "help": "Optional output file path",
                    "action": None,
                    "exclusive": False,
                },
                {
                    "name": "--force",
                    "help": "Automatically overwrite existing files",
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
    }
    return recipe

# --- Onboarding validation functions ---

# --- PLACEHOLDER ---

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    print()

    print_separator()

    print_footer()
