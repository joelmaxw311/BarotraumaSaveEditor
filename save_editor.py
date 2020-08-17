import gzip
import sys
import os
import argparse
import shutil


OPERATION_STRINGS = ['import', 'export']

TEMPORARY_FILES_PATH = './tmp/'
IMPORT_DIR_PATH = TEMPORARY_FILES_PATH + 'import/'
EXPORT_DIR_PATH = TEMPORARY_FILES_PATH + 'export/'
BACKUP_FILE_PATH = TEMPORARY_FILES_PATH + 'backup.save'

XML_FILE_PATH = IMPORT_DIR_PATH + 'save.xml'
BIN_FILE_PATH = IMPORT_DIR_PATH + 'save.bin'

EXPORT_FILE_PATH = EXPORT_DIR_PATH + 'export.rawsave'
EXPORT_SAVE_PATH = EXPORT_DIR_PATH + 'export.save'

SIZEOF_INT = 4
SIZEOF_CHAR = 2
BYTE_ORDER = 'little'

def parse_file(gz : gzip.GzipFile) -> (str, bytes):
    # read file title
    num_bytes = int.from_bytes(gz.read(SIZEOF_INT), byteorder=BYTE_ORDER)
    print(num_bytes)
    file_name : str = ""
    for i in range(num_bytes):
        file_name = file_name + chr(int.from_bytes(gz.read(SIZEOF_CHAR), byteorder=BYTE_ORDER))
    # read file data
    len_data = int.from_bytes(gz.read(SIZEOF_INT), byteorder=BYTE_ORDER)
    print(f"File {file_name} ({len_data} bytes)")
    file_data = gz.read(len_data)
    return file_name, file_data


def extract_save(save_file, dir_out) -> dict:
    file_map = {}
    with gzip.open(save_file, 'rb') as gz:
        print(len(gz.peek(SIZEOF_INT)))
        while(len(gz.peek(SIZEOF_INT)) >= SIZEOF_INT):
            file_name, file_data = parse_file(gz)
            file_map[file_name] = file_data
            with open(f"{dir_out}/{file_name}", 'wb+') as f:
                f.write(file_data) # write decompressed data to file_out
            print(len(gz.peek(SIZEOF_INT)))
    return file_map


def compress_save(dir_in, save_out):
    with gzip.open(save_out, 'wb+') as gz: 
        for file_in in os.listdir(dir_in):
            with open(f"{dir_in}/{file_in}", 'rb') as f:
                bdata = f.read() # read uncompressed data from file_in
            gz.write(int.to_bytes(len(os.path.basename(file_in)), SIZEOF_INT, byteorder=BYTE_ORDER)) # write length of file name
            for c in os.path.basename(file_in): # write file name
                gz.write(int.to_bytes(ord(c), SIZEOF_CHAR, byteorder=BYTE_ORDER))
            gz.write(int.to_bytes(len(bdata), SIZEOF_INT, byteorder=BYTE_ORDER)) # write length of file data
            gz.write(bdata) # write file data


def import_save(save_file):
    if not os.path.isdir(IMPORT_DIR_PATH):
        os.mkdir(IMPORT_DIR_PATH) # create IMPORT_DIR_PATH if it does not exist
    save_data : bytes = extract_save(save_file, IMPORT_DIR_PATH) # extract the .save file


def export_save(save_file):
    if not os.path.isdir(EXPORT_DIR_PATH):
        os.mkdir(EXPORT_DIR_PATH) # create EXPORT_DIR_PATH if it does not exist
    shutil.copyfile(save_file, BACKUP_FILE_PATH) # back up the .save file
    compress_save(IMPORT_DIR_PATH, EXPORT_SAVE_PATH) # compress to .save file
    shutil.copyfile(EXPORT_SAVE_PATH, save_file) # overwrite the .save file
    

def main(argv):
    parser = argparse.ArgumentParser(description='Modify Barotrauma .save files.')
    parser.add_argument('operation', type=str, choices=OPERATION_STRINGS, help='|'.join(OPERATION_STRINGS))
    parser.add_argument('save_file', type=str, help='.save file to open')
    args = parser.parse_args()

    operation : str = args.operation
    save_file : str = args.save_file

    if not os.path.isfile(save_file):
        print(f'File "{save_file}" does not exist')
        return 1

    if not save_file.endswith(".save"):
        print(f'"{save_file}" is not a .save file.')
        return 1

    if not os.path.isdir(TEMPORARY_FILES_PATH):
        os.mkdir(TEMPORARY_FILES_PATH) # create TEMPORARY_FILES_PATH if it does not exist

    if operation == 'import':
        import_save(save_file)
    elif operation == 'export':
        export_save(save_file)
    
    return 0

if __name__ == "__main__":
    retcode = main(sys.argv)
    sys.exit(retcode)
