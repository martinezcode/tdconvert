"""
Tests
"""

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

import tdconvert.properties
import tdconvert.library

if __name__ == "__main__":

    print_header(f"{__file__}")

    print_separator()

    # Test

    print_subheader(f"Testing Sample Data")

    profile = "test"
    overrides = None
    TestHub = tdconvert.properties.initialize_app(profile, overrides)
    database_populated = tdconvert.library.populate_sample_data(TestHub)
    print(f"Database populated: {database_populated}")

    print_separator()

    print_footer()
