# WoW Talent Parser

A parsing utility to be used alongside [Talent Extractor](https://github.com/snakybo/TalentExtractor) to provide talent and PvP talent data for [LibTalentInfo](https://github.com/snakybo/LibTalentInfo).

The usage chain of these three items is:

1. **WoW Talent Extractor** serializes talent and PvP talent data from in-game for manipulation out-of-game.
2. **WoW Talent Parsor parses (this)** parses the serialized data and converts it into a Lua table that is suitable for usage by LibTalentInfo.
3. **LibTalentInfo** injects the data back into the game as a library.

## Installation

This tool requires [Python 3](https://www.python.org/) and [py-lua-parser](https://github.com/boolangery/py-lua-parser).

## Usage

Copy the talent data generated by the [Talent Extractor](https://github.com/snakybo/TalentExtractor) addon at the `WTF/Account/YOUR ACCOUNT/SavedVariables/TalentExtractor.lua` into the same folder as the Python script, afterwards, run the `parse.py` script directly (or using the `parse.bat`) script to keep the command prompt open if an error occurs.

The script will generate a file called `TalentDataRetail.lua` which can be used to populate talent info provided by [LibTalentInfo](https://github.com/snakybo/LibTalentInfo).
