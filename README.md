# AppImageDesktop

`AppImageDesktop` is a Python command-line tool that simplifies the installation of AppImage applications on GNOME. It automates downloading, verifying, and installing AppImages while providing desktop integration through `.desktop` files. Inspired by the PKGBUILD approach, it uses a YAML configuration file to manage application details.

## Features

- **AppImage Desktop Integration**: Automatic shortcuts and icons using `.desktop` files.
- **Customizable Using YAML**: Easy configuration via YAML files.
- **Automatic Download**: Downloads AppImages automatically.
- **GPG Signature Verification (Optional)**: Optional verification for authenticity.

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

## Default Directories
`AppImageDesktop` uses specific directories for organizing installed applications. AppImages are stored in `~/appimages`, icons are placed in `~/.local/share/icons/`, and `.desktop` files are created in `~/.local/share/applications/`. This structure ensures that applications are easily accessible and integrated into the GNOME desktop environment.

## Uninstall

```
# find files
find . ~/.local/share/applications ~/.local/share/icons -iname "*obsidian*"
```

```
# delete files
find . ~/.local/share/applications ~/.local/share/icons -iname "*obsidian*" --delete
```