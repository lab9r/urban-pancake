#!/usr/bin/env python3

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from urllib.request import urlretrieve

import yaml

APPIMAGE_DIR = "~/appimages"
INSTALL_DIR =  "~/.local/share/applications"
THUMBNAIL_DIR = "~/.local/share/icons/"

def urlretrieve_wrapper(url, filename):

    def printProgress(blocknum, bs, size):
        percent = min((blocknum * bs) / size, 1.0)
        done = "#" * int(40 * percent)
        print(f'\rDownloading {filename}: [{done:<40}] {percent:.1%}', end='')

    urlretrieve(url, filename, printProgress)
    print(end='\r')
    print("")

class AppImgPkg:
    def __init__(self, pkg_file):
        with open(pkg_file) as fp:
            self.pkg = yaml.safe_load(fp)

        self._check_pkg()
                    
        self._parses_pkg()

        self.APPIMAGE_DIR = os.path.expanduser(APPIMAGE_DIR)
        self.INSTALL_DIR = os.path.expanduser(INSTALL_DIR)
        self.THUMBNAIL_DIR = os.path.expanduser(THUMBNAIL_DIR)

        for path in [self.APPIMAGE_DIR, self.INSTALL_DIR, self.THUMBNAIL_DIR]:
            os.makedirs(path, exist_ok=True)

    def _check_pkg(self):
        mandatory_keys = {"desktop_file", "desktop_replace", "icon", "pkgname", "pkgver", "source_url"}
        pkg_keys = set(self.pkg.keys())
        missing_keys = mandatory_keys.difference(pkg_keys)
        if "sha256sum" not in pkg_keys and "sha512sum" not in pkg_keys:
            missing_keys.add("sha{256,512}sum")
        if len(missing_keys) > 0:
            raise Exception(f"Missing keys: {', '.join(missing_keys)}")

    def _parses_pkg(self):
        self.pkg["source_url"] = self.pkg["source_url"].replace("$pkgver", self.pkg["pkgver"])

    def _download(self):
        source_url = self.pkg["source_url"]
        filename = source_url.split("/")[-1]
        dir_listing = os.listdir()
        if filename in dir_listing:
            print(f"{filename} already in directory - skipping download..")
        else:
            urlretrieve_wrapper(source_url, filename)
        
        # verify hashsum
        if "sha512sum" in self.pkg:
            hash_algo = "sha512sum"
            sha_hash = hashlib.sha512()
        else:
            hash_algo = "sha256sum"
            sha_hash = hashlib.sha256()
        
        with open(filename, "rb") as fp:
            for byte_block in iter(lambda: fp.read(4096), b""):
                sha_hash.update(byte_block)
            file_content = fp.read()
            sha_hash.update(file_content)
        if sha_hash.hexdigest() != self.pkg[hash_algo]:
            raise Exception(f"Hash verification failed for {filename}.")
        else:
            print(f"Hash verification successful for {filename}.")

        if "gpg_primary" in self.pkg:
            self._verify_gpg(filename)
        
        self.pkg["filename"] = filename

    def _verify_gpg(self, fn_appimage):
        for k in ["gpg_primary", "gpg_identity", "gpg_signature_url"]:
            if k not in self.pkg:
                raise Exception(f"Key {k} missing. Aborting gpg verification...")
        
        gpg_signature_url = self.pkg["gpg_signature_url"].replace("$pkgver", self.pkg["pkgver"])

        fn_sig = gpg_signature_url.split('/')[-1]
        urlretrieve_wrapper(gpg_signature_url, fn_sig)

        sig_valid = False
    
        try:
            # Run the gpg --verify command
            result = subprocess.run(
                ['gpg', '--verify', fn_sig, fn_appimage],
                capture_output=True,
                text=True,
                check=True
            )

            sig_valid = self.pkg["gpg_identity"] in result.stderr and \
            self.pkg["gpg_primary"] in result.stderr and \
            'BAD signature' not in result.stderr

        except subprocess.CalledProcessError as e:
            # Handle errors in the subprocess call
            print(f"Error running gpg:\n{e}")
            print(f"Output:\n{e.stdout}")
            print(f"Error Output:\n{e.stderr}")

        if sig_valid:
            print(f"gpg: Good signature for {fn_appimage}.")
        else:
            raise Exception(f"gpg: BAD signature for {fn_appimage}!")

    def install_appimage(self, debug=False):

        filename = self.pkg["filename"]
        appimage_path = os.path.realpath(filename)
        subprocess.run(["chmod", "u+x", appimage_path])

        appimagebin = os.path.join(self.APPIMAGE_DIR, self.pkg["pkgname"]) + ".AppImage"

        desktop_file_name = self.pkg["desktop_file"]

        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the AppImage to the temporary directory
            subprocess.run(
                [appimage_path, "--appimage-extract"],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.DEVNULL
            )
            if debug:
                print(f"temp_dir: {temp_dir}")
                import pdb
                pdb.set_trace()
            temp_dir = os.path.join(temp_dir, "squashfs-root")
            with open(os.path.join(temp_dir, desktop_file_name), "r") as fp:
                desktop_file = fp.readlines()
            
            to_replace = self.pkg["desktop_replace"].strip().split("\n")
            prefixes = [s.split("=")[0] + "=" for s in to_replace]

            # add icon stuff
            icon_filename = self.pkg["icon"].split("/")[-1].strip()
            icon_new_path = os.path.join(self.THUMBNAIL_DIR, icon_filename)

            prefixes.append("Icon=")
            to_replace.append("Icon=" + icon_new_path)

            for prefix, new_line in zip(prefixes, to_replace):
                for idx, line in enumerate(desktop_file):
                    if line.startswith(prefix):
                        desktop_file[idx] = new_line + "\n"

            new_desktop_file = "".join(desktop_file)
            new_desktop_file = new_desktop_file.replace("$appimagebin", appimagebin)

            # copy stuff

            # appimage
            shutil.copy(appimage_path, appimagebin)
            print(f"Copied {appimage_path} to {appimagebin}.")

            # icon
            # pdb.set_trace()
            shutil.copy(os.path.join(temp_dir, self.pkg["icon"]), icon_new_path)

            # desktop file
            with open(os.path.join(self.INSTALL_DIR, self.pkg["pkgname"] + ".desktop"), "w") as fp:
                fp.write(new_desktop_file)
        


def main():
    parser = argparse.ArgumentParser(description="A command-line tool that simplifies the installation of AppImage applications on GNOME.")
    parser.add_argument('config', type=str, nargs='?', help='Path to the yaml configuration file.')
    parser.add_argument('--config', type=str, help='Path to the yaml configuration file.')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (optional).')

    args = parser.parse_args()

    # Determine the config path
    if args.config is None:
        parser.error("The 'config' argument is required. Provide a value as a positional argument or with --config.")

    # Access the 'config' argument
    yml_path = args.config

    mgr = AppImgPkg(yml_path)
    mgr._download()
    mgr.install_appimage(debug=args.debug)

if __name__ == "__main__":
    main()