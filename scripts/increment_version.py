#!/usr/bin/env python
"""Increment version number by 0.1 before each build."""

import os

def main():
    # Get path to version.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(script_dir, '..', 'src', 'version.txt')

    # Read current version
    with open(version_file, 'r', encoding='utf-8') as f:
        current_version = f.read().strip()

    # Parse and increment by 0.1
    try:
        version_num = float(current_version)
        new_version = round(version_num + 0.1, 1)
    except ValueError:
        print(f"Error: Invalid version format '{current_version}', resetting to 1.0")
        new_version = 1.0

    # Write new version
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(str(new_version))

    print(f"Version incremented: {current_version} -> {new_version}")

if __name__ == '__main__':
    main()
