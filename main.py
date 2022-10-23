import argparse
import hashlib
import logging
import os
import shutil
from time import sleep


def sync_folders(source, replica):
    if not files_are_equal(source, replica):
        sync_files(replica, source)
    for f in os.scandir(source):
        if f.is_dir():
            make_folder_if_absent(f, replica)
            sync_folders(source + "\\" + f.name, replica + "\\" + f.name)
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


def sync_files(replica, source):
    check_delete(source, replica)
    check_copy(source, replica)


def check_delete(source, replica):
    for file_name in file_hashes(replica):
        if file_name not in file_hashes(source):
            delete_file(replica + "\\" + file_name)
            logging.info(f"Deleted file: {file_name} form replica directory.")


def delete_file(replica_path):
    try:
        os.remove(replica_path)
    except PermissionError:
        logging.error(f"Permission denied. Can't delete file: {replica_path}.")


def check_copy(source, replica):
    try:
        for file_name, file_hash in file_hashes(source).items():
            if file_name not in file_hashes(replica):
                copy_file(file_name, replica, source)
                logging.info(f"Copied new file {file_name} from source directory.")
            elif file_hash not in file_hashes(replica).values():
                copy_file(file_name, replica, source)
                logging.info(f"Updated file: {file_name} from source directory.")
    except PermissionError:
        logging.error(f"Permission error. Can't copy file at {source}.")


def copy_file(file_name, replica, source):
    shutil.copy2(source + "\\" + file_name, replica)


def make_folder_if_absent(f, replica):
    if f.name not in [r.name for r in os.scandir(replica) if r.is_dir()]:
        os.mkdir(replica + "\\" + f.name)


def delete_folder_if_absent_in_src(r, replica, source):
    if r.name not in [f.name for f in os.scandir(source) if f.is_dir()]:
        shutil.rmtree(replica + "\\" + r.name)


def parse_data():
    parser = argparse.ArgumentParser(prog="Python-File-Sync", description="Program that synchronizes folders.")
    parser.add_argument('source_dir', help="The path to the source folder.", type=str)
    parser.add_argument('replica_dir', help="The path to the replica folder. If it doesn't exist it'll "
                                            "be created.",
                        type=str)
    parser.add_argument('log_dir', help="The path to the log folder. If it doesn't exist, it'll be created.",
                        type=str)
    parser.add_argument('-ti', '--time_interval', dest="time_interval", help="The synchronization "
                                                                             "period in seconds.", type=int, default=60)
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
