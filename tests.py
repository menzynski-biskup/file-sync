import os
import pytest
from main import sync_folders, compute_md5


def test_sync_folders(tmp_path):

    source_directory = tmp_path / "source"
    source_directory.mkdir()
    sub_directory = source_directory / "subdir1"
    sub_directory.mkdir()
    file1 = source_directory / 'file1.txt'
    file2 = sub_directory / 'file2.txt'
    file1.write_text("This is test file.")
    file2.write_text("This is test file in subdir1")
    replica_directory = tmp_path / "replica"
    replica_directory.mkdir()
    file1_replica = replica_directory / "file1.txt"
    file2_replica = replica_directory / "subdir1" / "file2.txt"

    # test copying new files
    sync_folders(source_directory, replica_directory)

    assert os.listdir(source_directory) == os.listdir(replica_directory)
    assert os.listdir(sub_directory) == os.listdir(replica_directory / 'subdir1')
    assert compute_md5(file1) == compute_md5(file1_replica)
    assert compute_md5(file2) == compute_md5(file2_replica)

    # test deleting file from replica directory
    os.remove(file1)
    sync_folders(source_directory, replica_directory)
    assert os.listdir(source_directory) == os.listdir(replica_directory)
    assert os.listdir(sub_directory) == os.listdir(replica_directory / 'subdir1')

    # test copy edited file
    file2.write_text("This file was edited.")
    sync_folders(source_directory, replica_directory)
    assert compute_md5(file2) == compute_md5(file2_replica)


if __name__ == '__main__':
    pytest.main()
