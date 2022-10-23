# file-sync
## Program for folder synchronization.

### Program description
This program provides one-way synchronization for files and folders 
in source directory with backup directory. This program creates new folders,
copies existing files, detects if file was edited and updates it, and deletes
files that are no longer present in source directory. It provides synchronization 
in given time intervals.

This program needs four arguments at start as console input to work properly.

- source directory path
- replica directory path
- logs directory path
- time interval in seconds _(optional)_ - if it's not given it takes default value - 60 seconds.
### Starting program
To start program you need to open console in file-sync directory and run main.py file
giving arguments in the order as you see it above. For example, it can look like that:

    python main.py "C:\source_directory" "C:\replica_directory" "C:\log_directory" -ti 20

The source, replica and log directory paths are obligatory - without them program won't start. 
Also, the source directory path must be a path to existing directory, when replica and log 
directories will be created if they don't exist.

### Additional info
This project is written in Python 3.9 using PyCharm IDE as example project. 
It is not fully functional program and should be used carefully.