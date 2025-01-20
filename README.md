# AppImageDesktop

`AppImageDesktop` is a Python command-line tool that simplifies the installation of AppImage applications on GNOME. It automates downloading, verifying, and installing AppImages while providing desktop integration through `.desktop` files. Inspired by the PKGBUILD approach, it uses a YAML configuration file to manage application details.

## Features

- **Download AppImage**: Fetches AppImage files from specified URLs.
- **Hash Verification**: Validates file integrity using SHA256 or SHA512 checksums.
- **GPG Signature Verification (optional)**: Confirms AppImage authenticity via GPG signatures.
- **Desktop Entry Creation**: Generates `.desktop` files for easy application launching.
- **Icon Management**: Copies application icons to the appropriate directory.
- **YAML Configuration**: Easily add install scripts using yaml.

## Usage

Create a YAML configuration file for the AppImage you want to install. For examples see `configs` directory.

```
usage: AppImageDesktop.py [-h] [--config CONFIG] [--debug] [config]

positional arguments:
  config           Path to the yaml file.

options:
  --config CONFIG  Path to the yaml file.
  --debug          Enable debug mode (optional).
```

### Example

```
python3 AppImageDesktop.py configs/obsidian.yaml
```


## ubuntu dependency
This is for AppImages in general, not specific to this project.

```
sudo apt install libfuse2 -y
 ```

## uninstall

```
# find files
find . ~/.local/share/applications ~/.local/share/icons -iname "*obsidian*"

# delete files
find . ~/.local/share/applications ~/.local/share/icons -iname "*obsidian*" --delete
```