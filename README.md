# WoW Talent Parser

A parsing utility to be used alongside [Talent Extractor](https://github.com/snakybo/TalentExtractor). It's able to parse the raw class, specialization, and talent data, and produce a usable, common interface for accessing it.

## Installation

This tool requires [Python 3](https://www.python.org/).

## Usage

Run `parse-talents.py` (required arguments below).

### Within VS Code

This repo ships with VS Code launch configurations for every WoW expansion, so you can run the script directly from the editor. Simply select the appropriate expansion and run the configuration. You'll be prompted for the path to the your `TalentExtractor.lua` file, after that a new file in the `out/` directory will be created with the parsed talent data.

## parse-talents.py

The available command-line arguments are:

Argument         | Required | Description
--------         | -------- | -----------
`--output`       | Yes      | The output .lua file
(positional)     | Yes      | The input TalentExtractor.lua file

### Example

```python
py ./parse-talents.py --output "out/TalentDataWrath.lua" TalentExtractor.lua
```
