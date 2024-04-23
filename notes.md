## Structuring script

    1) copy files and be sure exactly match content of the source folder
        # create argument logic

        # if exists on TARGET AND SOURCE not, remove from TARGET
        # if exists on SOURCE and TARGET, compare sizes, compare hashes (SHA1)

    2) synchronization should be performed in periods (in the argument have seconds, and sleep for that)

    3) Log to file (created, copied, removed), console output

    4) Path for log file, and sync interval in the arguments (timestamp or date time)


## Future improvements

    - if files are still being created/edit, we need to "lock"(skip that file)
    - add more tests to ensure code quality
