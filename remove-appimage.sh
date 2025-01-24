#!/bin/bash

# Help function
function show_help {
    echo "Usage: $(basename "$0") <pkgname>"
    echo
    echo "This script searches for files related to the specified package name in the following directories:"
    echo "  - ~/appimages"
    echo "  - ~/.local/share/applications"
    echo "  - ~/.local/share/icons"
    echo
    echo "If matching files are found, the user will be prompted to confirm deletion of these files."
    echo
    echo "Arguments:"
    echo "  pkgname    The name or part of the name of the package to search for."
    echo
    echo "Examples:"
    echo "  $(basename "$0") obsidian"
    echo
    echo "Note: This action is irreversible. Use with caution."
    exit 0
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
fi



if [ -z "$1" ]; then
    echo "Please provide a command-line argument to replace 'pkgname'."
    exit 1
fi

results=$(find ~/appimages ~/.local/share/applications ~/.local/share/icons -iname "*$1*")


if [ -n "$results" ]; then
    echo "Found matching files:"
    for file in $results; do
        echo "$file"
    done
else
    echo "No matching files found."
    exit 0
fi


read -p "Do you want to delete all these files? (y/n) "

if [ "$REPLY" == "y" ]; then
for file in $results; do
    echo "Deleting: $file"
    rm "$file"
done
echo "All matching files have been deleted."
else
    echo "Deletion canceled."
fi