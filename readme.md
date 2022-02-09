# Time Interval Counter Logger (TIC Logger)
## Objects
Log and store measurements from various time interval counters.

## Supported TICs
- Keysight 53230A
- Keysight 53132A
- Keysight 53131A
- Stanford Research Systems SR620

## Available measurement configurations
- Measuring frequency on ch1 or ch2.
- Measuring time interval between ch1 and ch2.

## How to run this program
1. Modify "src/main.ini" file.
2. Run "src/main.py" file.
3. Check "outputs/measurements/" for measurements and "outputs/logs/" for logs.

## How to modify for more queries/instructions
- To modify or add SCPI instructions, change "apply_presets.py" in "src/subfunctions".
