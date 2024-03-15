# Anime Cursors

Python library wrapper for [cursorgen](https://github.com/ashuramaruzxc/cursorgen) for building animated
and static cursors primarily made by [[夜夢（よるむ)](https://www.pixiv.net/en/users/345405)]

## Requirements

* Python version 3.7.5 or higher
* [cursorgen](https://github.com/ashuramaruzxc/cursorgen) >= 1.0.0

## Installation

### Python

* Clone the repo
* `pip install cursorgen -e https://github.com/ashuramaruzxc/cursorgen#egg=cursorgen`

### NixOS/Nix

* Clone the repo
* Ensure that `nix >= 2.37` is installed
* in`nix.conf` put `experimental-features = nix-command flakes`
* `nix-env -iA nixpkgs.direnv`
* `direnv allow`

## Usage

If you have animated or static (.ani | .cur) files you can simply run:

    python -m CursorConverter --prefix /Path/To/Directory With Cursors
It will create a directory `dist` with cursorname directory, thumbnail and simple index.theme file

However, if you want to make a custom name and add a comment:

    python -m CursorConverter \
    --prefix /Path/To/Directory With Cursors \
    --name "Sample" \
    --comment "Sample"
You can also specify amount of jobs(something like make -j16...) in order to speed up converter a bit:

    python -m CursorConverter --prefix /Path/To/Directory With Cursors -j numberOfJobs

## Media Assets

This project utilizes media assets that are created by [夜夢（よるむ)](https://www.pixiv.net/en/users/345405), who gave permission to modify and redistribute their work.

Please note that if you plan to use or redistribute these assets, you must adhere to the terms of the license. See the [LICENSE](COPYING.CC-BY-NC-SA.4.0.md) file for details.

## Credits

* Media Assets by: 夜夢（よるむ)
* [Author's Pixiv Profile](https://www.pixiv.net/en/users/345405)
* Some cursors were ported by [muha0644](https://www.pling.com/u/muha0644), which were used as reference.
  
## Contact

* [ashuramaru@tenjin-dk.com](mailto:ashuramaru@tenjin-dk.com)
