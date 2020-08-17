# Barotrauma Save Editor
Modify .save files of the game Barotrauma

On Windows, Barotrauma .save files are located at

    %LOCALAPPDATA%\Daedalic Entertainment GmbH\Barotrauma

# Usage
There are two ways to execute the script: non-interactive or interactive. 

## Non-Interactive Mode
Run the tool from the shell, providing parameters as command arguments.

    python save_editor.py [[-h] {import,export} save_file_path]

### Show command help
    python save_editor.py -h

### Decompress a .save file
Extract gamesession.xml and .sub files from a .save file to ./tmp/import/

    python save_editor.py import "path/to/save/file.save"

Edit gamesession.xml and add copy .sub files to ./tmp/import/ to modify the save data.

### Recompress files to a .save file
Compress modified save data from ./tmp/import/ to a Barotrauma .save file.

    python save_editor.py export "path/to/save/file.save"

## Interactive mode
Executing the save_editor.py directly (i.e. double-clicking save_editor.py in the file browser) without providing command-line arguments will run the tool in interactive mode.
In interactive mode, the program will prompt the user to enter each parameter.

    > ./save_editor.py
    import or export:
    import
    file path:
    path/to/save/file.save
