# TD Convert

**Technical Document Conversion Tool**

Converts technical document files between various formats.

## Usage

### Load conversion instructions

Use JSON to define conversion instructions for a file format.

#### Create JSON instructions

##### Single format mapping example

This mapping will convert:

- markdown files to rtf and txt

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

##### Multiple format mapping example

These mappings will convert:

- json files to docx and html
- markdown files to rtf and txt

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

#### Create foo.docx and foo.html from foo.json

```
tdconvert convert --input foo.json
```

#### Create foo.rtf and foo.txt from foo.md

```
tdconvert convert --input foo.md
```

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

## Clone this repo

<https://github.com/martinezcode/tdconvert.git>

## Enter the directory for this repo

```
cd /path/to/tdconvert
```

## Install dependencies

```
pip install -r requirements.txt
```

## Install this app

> [!IMPORTANT]
> **This step is required to enable running in the terminal with app commands.**
>
> Imports will fail if the `.py` files are run directly without first installing your package as a module. Debugging in an IDE outside the virtual environment may require additional configuration or running with `python -m`.

> [!TIP]
> Use the `-e` flag to install in editable mode for development changes to take effect in real time.

```
pip install -e .
```

## Run initial test

##### Display welcome screen

```
tdconvert
```

##### Run environment tests

```
tdconvert test
```

## Convert files

#### After installation, follow the usage instructions above to convert files
