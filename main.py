import argparse
import hashlib
import logging
import os
import shutil
from time import sleep


class SyncFiles:

    def __init__(self, source, replica):
        self.source = source
        self.replica = replica

    def check_delete(self):
        for file_name in file_hashes(self.replica):
            if file_name not in file_hashes(self.source):
                SyncFiles.delete_file(self.replica + "\\" + file_name)
                logging.info(f"Deleted file: {file_name} form replica directory.")

    def delete_file(self):
        try:
            os.remove(self.replica)
        except PermissionError:
            logging.error(f"Permission denied. Can't delete file: {self.replica}.")

    # Check_copy function checks which file is new by comparing file names between source and replica.
    # Then it copies the missing files to replica directory.
    # It also checks file hashes to find files that was edited and copy them.

    def check_copy(self):
        try:
            for file_name, file_hash in file_hashes(self.source).items():
                if file_name not in file_hashes(self.replica):
                    SyncFiles.copy_file(self, file_name)
                    logging.info(f"Copied new file {file_name} from source directory.")
                elif file_hash not in file_hashes(self.replica).values():
                    SyncFiles.copy_file(self, file_name)
                    logging.info(f"Updated file: {file_name} from source directory.")
        except PermissionError:
            logging.error(f"Permission error. Can't copy file at {self.source}.")

    def copy_file(self, file_name):
        shutil.copy2(str(self.source) + "\\" + file_name, self.replica)


# Function sync_folders that checks if files in source directory are the same as in replica
# - if not it synchronizes changes and new files.
# Then function checks if folders in source directory are the same as in replica
# - if not it creates new folder in replica and moves to that directory,
# where it repeats file synchronization and folder synchronization process.
# Function also checks if folder in source directory was deleted and removes it from replica directory.

def sync_folders(source, replica):
    if not files_are_equal(source, replica):
        SyncFiles(source, replica).check_copy()
        SyncFiles(source, replica).check_delete()
    for f in os.scandir(source):
        if f.is_dir():
            make_folder_if_absent(f, replica)
            sync_folders(str(source) + "\\" + f.name, str(replica) + "\\" + f.name)
    for r in os.scandir(replica):
        if r.is_dir():
            delete_folder_if_absent_in_src(r, replica, source)


def files_are_equal(source, replica):
    return file_hashes(source) == file_hashes(replica)


def file_hashes(directory):
    hash_dict = dict()
    for f in os.scandir(directory):
        if f.is_file():
            hash_dict[f.name] = compute_md5(f.path)
    return hash_dict


def compute_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for bytes_piece in iter(lambda: f.read(4096), b""):
                hash_md5.update(bytes_piece)
        return hash_md5.hexdigest()
    except PermissionError:
        logging.error(f"Permission error for file at {file_path}")


def make_folder_if_absent(f, replica):
    if f.name not in [r.name for r in os.scandir(replica) if r.is_dir()]:
        os.mkdir(str(replica) + "\\" + f.name)


def delete_folder_if_absent_in_src(r, replica, source):
    if r.name not in [f.name for f in os.scandir(source) if f.is_dir()]:
        shutil.rmtree(replica + "\\" + r.name)


def parse_data():
    parser = argparse.ArgumentParser(prog="Python-File-Sync",
                                     description="Program that synchronizes folders.")
    parser.add_argument('source_dir', help="The path to the source folder.", type=str)
    parser.add_argument('replica_dir', help="The path to the replica folder. If it "
                                            "doesn't exist it'll be created.", type=str)
    parser.add_argument('log_dir', help="The path to the log folder. If it doesn't "
                                        "exist, it'll be created.", type=str)
    parser.add_argument('-ti', '--time_interval', dest="time_interval",
                        help="The synchronization period in seconds.", type=int, default=60)
    args = parser.parse_args()
    return args.source_dir, args.replica_dir, args.log_dir, args.time_interval


def check_src_path(path):
    if not os.path.exists(path):
        logging.error(f"Error - directory not found: {path}")
        exit()


def check_create_path(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except FileNotFoundError:
        logging.error(f"Error - directory not found: {path}")
        exit()


if __name__ == "__main__":

    src, rep, logs, interval = parse_data()

    check_create_path(logs)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(logs + "\\" + "logs.txt"),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Starting folder synchronization.\n"
                 f"Source directory: {src}\n"
                 f"Replica directory: {rep}\n"
                 f"Log directory: {logs}\n"
                 f"Synchronization period: every {interval} seconds.")
    while True:
        check_src_path(src)
        check_create_path(rep)
        logging.info(f"Starting synchronization.")
        sync_folders(src, rep)
        logging.info("Synchronization ended.")
        sleep(interval)
