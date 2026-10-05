# Anime Cursors

Animated anime cursor themes for Linux, using artwork by
[夜夢（よるむ）](https://www.pixiv.net/en/users/345405). This project downloads
the artist's Windows `.ani` cursors and converts them into installable Xcursor
themes with [cursorgen](https://github.com/ashuramaruzxc/cursorgen).

## Install a theme

On Linux, install [uv](https://docs.astral.sh/uv/getting-started/installation/)
and Git, then clone the repository and install its dependencies. uv manages
Python 3.14 for you.

```sh
git clone https://github.com/ashuramaruzxc/anime-cursors.git
cd anime-cursors
uv python install
uv sync --locked
```

Build and install Hakurei Reimu's theme:

```sh
uv run --locked python process_cursors.py \
  --theme hakurei-reimu --format directory --jobs 4
mkdir -p ~/.local/share/icons
cp -a dist/anime-hakurei-reimu ~/.local/share/icons/
```

Select **Hakurei Reimu** in your desktop's cursor settings. Its theme directory
is `anime-hakurei-reimu`; use that name when configuring a cursor theme by ID.
If applications keep showing the old cursor, log out and back in.

### Choose another theme

List theme IDs and any missing cursor roles:

```sh
uv run --locked python process_cursors.py --list
```

Replace `hakurei-reimu` in the build and copy commands with your chosen ID. Only
themes with an empty `missing_roles` list can be built. Repeat `--theme` to
select several themes, or omit it to build all complete themes.

Builds download and cache the required artwork automatically. Without
`--format directory`, they produce `dist/<theme-id>.zip`; extract each ZIP into
`~/.local/share/icons/anime-<theme-id>/` to install it.

## Nix

On Linux with flakes enabled, run these commands from the repository checkout:

```sh
nix build .#anime-hakurei-reimu
mkdir -p ~/.local/share/icons
cp -aL result/share/icons/anime-hakurei-reimu ~/.local/share/icons/
```

Select the theme in your desktop settings as above. Use `#anime-cursors` instead
to build all complete themes.

### NixOS or Home Manager

Add the checkout to your configuration flake, replacing the path below with its
absolute path:

```nix
inputs.anime-cursors.url = "path:/absolute/path/to/anime-cursors";
```

Pass `inputs` through `specialArgs` (or Home Manager's `extraSpecialArgs`), then
add this module to your configuration:

```nix
{ inputs, lib, ... }:
{
  imports = [ inputs.anime-cursors.nixosModules.default ];

  nixpkgs.config.allowUnfreePredicate =
    pkg: lib.hasPrefix "anime-cursors" (lib.getName pkg);

  programs.anime-cursors = {
    enable = true;
    theme = "hakurei-reimu";
    size = 32;
  };
}
```

For Home Manager, use `inputs.anime-cursors.homeManagerModules.default` instead.
If you already have an unfree predicate, extend it to allow these packages. With
Home Manager's `useGlobalPkgs`, set it in NixOS instead.

The NixOS module sets session defaults and SDDM's cursor; desktop settings can
override them. Home Manager configures `home.pointerCursor`; enable `gtk.enable`
to apply its GTK settings. Rebuild your configuration and log in again to load
the session defaults.

## Convert your own cursors

After the uv setup above, convert a complete directory of `.ani` files:

```sh
uv run --locked python -m CursorConverter \
  --prefix /path/to/cursors --name Sample --jobs 4
```

The output is `dist/Sample/`. Filenames must match the [default role
mapping](CursorConverter/config/definitions_jp.json), or a custom mapping
supplied with `--json`. Use `--help` for all converter options.

## Credits and license

Cursor artwork by [夜夢（よるむ）](https://www.pixiv.net/en/users/345405),
redistributed with permission under CC BY-NC-SA 4.0. Conversion code is GPLv3;
see [LICENSE](LICENSE) and the author notices included with built themes.
Earlier ports by [muha0644](https://www.pling.com/u/muha0644) served as a
reference.

## Contact

For questions or abuse reports, contact
[ashuramaru@tenjin-dk.com](mailto:ashuramaru@tenjin-dk.com).
