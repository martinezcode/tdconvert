# TD Convert

**Technical Document Conversion Tool**

## About the Project

**TD Convert** is command line utility that converts technical document files between various formats.

### Built With

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)

## Key Features

- Enables automated file conversion workflows based on simple input/output format mappings.
- Converts to multiple output files in different formats with a single command.
- Supports conversion to and from several common technical document formats like: `Markdown`, `Microsoft Word DOCX`, `HTML`, `CSV`, `JSON`, `RTF`, and `TXT`.
- Leverages the trusted [Pandoc](https://pandoc.org) command line tool and [pypandoc](https://github.com/JessicaTegner/pypandoc) `Python` library for reliable file format conversions.
- Imports conversion instructions from self-documenting `JSON`. Input/output format mappings are:
  - Easy to read and write in plain text
  - Simple to create and modify programmatically
  - Ready for batch processing
  - Version control friendly
- Profile based settings make it easy to define distinct output options for different workflows involving the same input file types.
- Automatically handles existing file conflicts. The `conflict_option` instruction tells the app what to do if the output files exist: `overwrite`, `rename`, or `prompt`.
- Includes a dry run mode that traverses the full conversion path without actually reading or writing files. Perfect for fast workflow tests and conversion simulations.
- Built with an extensible architecture for easy implementation of new file formats and conversion engines.

## Usage

### Load conversion instructions

Use JSON to define conversion instructions for a file format.

#### Create JSON instructions

##### Example: Single format mapping

This mapping will convert:

- `markdown` files to `rtf` and `plain` text

```json
{
    "profile_id": "default",
    "format_id": "markdown",
    "engine_id": "markdown_strict",
    "output_format_ids": [
        "rtf",
        "plain"
    ],
    "output_engine_ids": [
        "pandoc",
        "pandoc"
    ],
    "output_extension_ids": [
        ".rtf",
        ".txt"
    ],
    "conflict_option": "overwrite"
}
```

##### Example: Multiple format mappings

These mappings will convert:

- `json` files to `docx` and `html`
- `markdown` files to `rtf` and `plain` text

```json
[
    {
        "profile_id": "default",
        "format_id": "json",
        "engine_id": "pandoc",
        "output_format_ids": [
            "docx",
            "html"
        ],
        "output_engine_ids": [
            "pandoc",
            "pandoc"
        ],
        "output_extension_ids": [
            ".docx",
            ".html"
        ],
        "conflict_option": "overwrite"
    },
    {
        "profile_id": "default",
        "format_id": "markdown",
        "engine_id": "markdown_strict",
        "output_format_ids": [
            "rtf",
            "plain"
        ],
        "output_engine_ids": [
            "pandoc",
            "pandoc"
        ],
        "output_extension_ids": [
            ".rtf",
            ".txt"
        ],
        "conflict_option": "overwrite"
    }
]
```

#### Import JSON instructions

```
tdconvert load --json instructions.json
```

### Convert files

After importing the instructions, use `tdconvert convert --input` to convert files.

The app will auto-detect the input file format and perform the mapped conversions.

#### Create `foo.docx` and `foo.html` from `foo.json`

```
tdconvert convert --input foo.json
```

#### Create `foo.rtf` and `foo.txt` from `foo.md`

```
tdconvert convert --input foo.md
```

### Dry run workflow tests

#### Simulate conversion to `foo.rtf` and `foo.txt` from `foo.md` without touching files

```
tdconvert convert --input foo.md --dry
```

### Create conversion profiles

Use `--profile` to convert the same file types with different workflow instructions.

No setup is required, a new profile will automatically be created the first time you use it. A profile named `default` is used when running without the `--profile` flag.

#### Example: Convert markdown files to different formats for various workflows

##### Load `default` profile

```
tdconvert load --json default_instructions.json
```

##### Load custom profiles: `blog`, `website`, `resume`
```
tdconvert --profile blog load --json blog_instructions.json

tdconvert --profile website load --json website_instructions.json

tdconvert --profile resume load --json resume_instructions.json
```

##### Convert with `default` profile

```
tdconvert convert --input normal_content.md
```

##### Convert with custom profiles: `blog`, `website`, `resume`

```
tdconvert --profile blog convert --input blog_post.md

tdconvert --profile website convert --input web_content.md

tdconvert --profile resume convert --input job_resume.md
```

> [!TIP]
> The profile name must be the first argument to `tdconvert`. Place `--profile` before the `load` or `convert` commands.

## Roadmap

Additional features are planned for implementation in the near future:

- UI for interactively creating and updating mapping instructions
- PDF support
- Word theme template support
- More file formats
- Custom Pandoc arguments
- Advanced file rename options
- Output folder customization

## License

**TD Convert** is distributed under the MIT license. See `LICENSE.txt` for details.

## Installation

### Install System Dependency

> [!IMPORTANT]
> Installing the [Pandoc](https://pandoc.org/index.html) command-line tool is required for document conversion.

##### macOS (Homebrew):

```
brew install pandoc
```

##### Linux:

```
sudo apt-get install pandoc
```

##### Windows:

[Download and Run Installer](https://pandoc.org/installing.html)

### Install Framework Dependency

> [!IMPORTANT]
> Installing the [Pza Framework](https://github.com/martinezcode/pza) python module is required for running this app.

##### Clone the Pza framework repo

<https://github.com/martinezcode/pza.git>

##### Install the Pza framework

> [!TIP]
> Use the `-e` flag to install in editable mode for framework changes to take effect in real time.

```
pip install -e '/path/to/pza'
```

### Install TD Convert

##### Clone this repo

<https://github.com/martinezcode/tdconvert.git>

##### Enter the directory for this repo

```
cd /path/to/tdconvert
```

##### Install dependencies (pypandoc)

```
pip install -r requirements.txt
```

##### Install this app

> [!IMPORTANT]
> **This step is required to enable running in the terminal with app commands.**
>
> Imports will fail if the `.py` files are run directly without first installing your package as a module.
>
> Debugging in an IDE with a different interpreter or outside of the installation environment may require additional configuration or running with `python -m`.

> [!TIP]
> Use the `-e` flag to install in editable mode for development changes to take effect in real time.

```
pip install -e .
```

##### Run initial test

###### Display welcome screen

```
tdconvert
```

###### Run environment tests

```
tdconvert test
```

##### Convert files

After installation, follow the usage instructions above to convert files.

## Contact

Aaron Martinez is on LinkedIn: [@martinezcode](https://www.linkedin.com/in/martinezcode/)
