import gzip
import sys
import os
import argparse
import shutil
import logging


OPERATION_STRINGS = ['import', 'export']

TEMPORARY_FILES_PATH = './tmp/'
IMPORT_DIR_PATH = TEMPORARY_FILES_PATH + 'import/'
EXPORT_DIR_PATH = TEMPORARY_FILES_PATH + 'export/'

SIZEOF_INT = 4
SIZEOF_CHAR = 2
BYTE_ORDER = 'little'


# Read the next string value from GzipFile object "gz"
def gzip_parse_string(gz):
    num_bytes = int.from_bytes(gz.read(SIZEOF_INT), byteorder=BYTE_ORDER)
    s = ""
    for i in range(num_bytes):
        s = s + chr(int.from_bytes(gz.read(SIZEOF_CHAR), byteorder=BYTE_ORDER))
    return s


# Read the next block of bytes from GzipFile object "gz"
def gzip_parse_bytes(gz):
    len_data = int.from_bytes(gz.read(SIZEOF_INT), byteorder=BYTE_ORDER)
    file_data = gz.read(len_data)
    return file_data


# Parse multiple files from GzipFile object "gz"
def gzip_parse_file(gz):
    # read file title
    file_name = gzip_parse_string(gz)
    # read file data
    file_data = gzip_parse_bytes(gz)
    return file_name, file_data


# Write string value "strval" to GzipFile object "gz"
def gzip_write_string(gz, strval):
    # write length of string
    gz.write(int.to_bytes(len(strval), SIZEOF_INT, byteorder=BYTE_ORDER)) 
    # write string characters
    for c in strval: 
        gz.write(int.to_bytes(ord(c), SIZEOF_CHAR, byteorder=BYTE_ORDER))


# Write bytes of "bdata" to GzipFile object "gz"
def gzip_write_bytes(gz, bdata):
    gz.write(int.to_bytes(len(bdata), SIZEOF_INT, byteorder=BYTE_ORDER)) # write length of file data
    gz.write(bdata) # write file data


# Decompress and extract all files from a .save file
# The .save file will contain one .xml and one or more .sub files.
# Write imported files to ./tmp/import/
def extract_save(save_file):
    file_map = {}
    with gzip.open(save_file, 'rb') as gz:
        while(len(gz.peek(SIZEOF_INT)) >= SIZEOF_INT):
            file_name, file_data = gzip_parse_file(gz)
            file_map[file_name] = file_data
    return file_map


# Compress and write all files in directory "dir_in" to one .save file "save_out"
def compress_save(dir_in, save_out):
    with gzip.open(save_out, 'wb+') as gz: 
        for file_in in os.listdir(dir_in):
            with open(f"{dir_in}/{file_in}", 'rb') as f:
                bdata = f.read() # read uncompressed data from file_in
            file_name = os.path.basename(file_in)
            gzip_write_string(gz, file_name)
            gzip_write_bytes(gz, bdata)


# Validate a .save file "save_out" against files in directory "dir_in".
# Ensure that the file names and decompressed file contents of the .save file "save_out" match the 
# names and contents of files in directory "dir_in".
# Returns True if the .save is valid, or False if the .save is invalid.
def validate_save(dir_in, save_out):
    validated_files : dict = extract_save(save_out) # extract files data from .save file
    for file_in in os.listdir(dir_in): # for each file in directory "dir_in"
        if not file_in in validated_files: # file name not found in .save archive
            return False # .save file is invalid: missing file
        with open(f"{dir_in}/{file_in}", 'rb') as f:
            bdata = f.read() # read uncompressed data from file_in
        if not bdata == validated_files[file_in]: # raw file data does not match data extracted from .save
            return False # .save file is invalid: inconsistent file contents
    return True # .save file is valid


# Decompress files from .save file "save_file" to separate files in directory "dir_in"
def import_save(save_file):
    # create IMPORT_DIR_PATH if it does not exist
    if not os.path.isdir(IMPORT_DIR_PATH):
        os.makedirs(IMPORT_DIR_PATH) 
    save_data = extract_save(save_file) # extract files data fom the .save file
    # write decompressed files
    for file_name, file_data in save_data.items():
        print(f"{file_name}: {len(file_data) if file_data is not None else file_data} bytes")
        with open(f"{IMPORT_DIR_PATH}/{file_name}", 'wb+') as f:
            f.write(file_data) # write decompressed data to imported file


# Compress and write all files in directory "dir_in" to one .save file "save_file"
def export_save(save_file):
    # create EXPORT_DIR_PATH if it does not exist
    if not os.path.isdir(EXPORT_DIR_PATH):
        os.makedirs(EXPORT_DIR_PATH)
    path_in = IMPORT_DIR_PATH # path of imported files directory
    path_out = EXPORT_DIR_PATH + save_file # path of temporary .save file to create
    compress_save(path_in, path_out) # compress to a temporary .save file
    validate_save(path_in, path_out) # ensure that the created 
    shutil.copyfile(path_out, save_file) # overwrite "save_file"


def main(argv):
    parser = argparse.ArgumentParser(description='Modify Barotrauma .save files.')
    parser.add_argument('operation', type=str, choices=OPERATION_STRINGS, help="Import from or export to a .save file.")
    parser.add_argument('save_file', type=str, help='A .save file to open.')
    args = parser.parse_args()

    operation = args.operation
    save_file = args.save_file

    if not os.path.isfile(save_file):
        print(f'File "{save_file}" does not exist')
        return 1

    if not save_file.endswith(".save"):
        print(f'"{save_file}" is not a .save file.')
        return 1

    if not os.path.isdir(TEMPORARY_FILES_PATH):
        os.mkdir(TEMPORARY_FILES_PATH) # create TEMPORARY_FILES_PATH if it does not exist

    if operation == 'import':
        import_save(save_file) # import from a .save
    elif operation == 'export':
        export_save(save_file) # export to a .save
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # without command-line args (prompt for parameters)
        try:
            print("import or export:")
            operation = input()
            print("file path:")
            save_file = input().strip("\"")
            if operation == 'import':
                import_save(save_file)
            elif operation == 'export':
                export_save(save_file)
        except Exception as e:
            logging.error('Error at %s', 'division', exc_info=e)
            input()
    else:
        # with command-line args
        retcode = main(sys.argv)
        sys.exit(retcode)
