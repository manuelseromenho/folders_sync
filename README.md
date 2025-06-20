# Folder Synchronization Script

Author: Manuel Seromenho
Date: 2025-06-20

## Overview
Synchronizes files from a SOURCE folder to a TARGET folder. It ensures that the TARGET folder is an identical copy of the SOURCE folder by periodically synchronizing the contents.

## Usage
To run the script, use the following command format:

```
python -m src <source_path> <target_path> <sync_period> <sync_amount> <log_file>
```

### Parameters:
- `<source>`: Path to the source folder (e.g., `"source"`)
- `<target>`: Path to the target folder (e.g., `"target"`)
- `<sync_period>`: Synchronization period in seconds (e.g., `10`)
- `<sync_amount>`: Amount of synchronizations (e.g., `5`)
- `<log_file>`: Path to the logging file (e.g., `log1.txt`)

### Example Command:
```bash
python -m src source_path target_path 10 5 log1.txt
```

## Logging
All operations (file creation, copying, and removal) are logged both to the console and to the specified log file, providing full transparency of the synchronization process.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
