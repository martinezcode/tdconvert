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
            "file_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "input_file": "TEXT",
            "timestamp": "DATETIME",
        }
    }
    return recipe

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
