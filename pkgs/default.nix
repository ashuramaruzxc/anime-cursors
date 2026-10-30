{
  lib,
  newScope,
  python314Packages,
  fetchurl,
  cursorgenSrc,
}:
let
  lock = lib.trivial.importTOML ../uv.lock;
  fromLock =
    package: repository:
    let
      source = lib.lists.findFirst (
        entry: entry.name == package.pname
      ) (throw "Missing ${package.pname} in uv.lock") lock.package;
    in
    if lib.strings.versionAtLeast package.version source.version then
      package
    else
      package.overridePythonAttrs (old: {
        inherit (source) version;
        src = fetchurl {
          inherit (source.sdist) url;
          hash = source.sdist.hash;
        };
        meta = old.meta // {
          changelog = "https://github.com/${repository}/releases/tag/${source.version}";
        };
      });
in
lib.customisation.makeScope newScope (self: {
  # Scope the newer dependencies so transitive consumers use the same versions
  pythonPackages = python314Packages.overrideScope (
    _: prev: {
      msgspec = (fromLock prev.msgspec "jcrist/msgspec").overridePythonAttrs (old: {
        # The 0.22.0 release includes this big-endian fix
        patches = lib.lists.filter (
          patch: (patch.name or "") != "0001-msgspec-Fix-backing-type-declaration-of-Ext.code.patch"
        ) (old.patches or [ ]);
      });
      platformdirs = fromLock prev.platformdirs "tox-dev/platformdirs";
    }
  );

  cursorgen = self.pythonPackages.callPackage ./cursorgen.nix { src = cursorgenSrc; };
  converter = self.pythonPackages.callPackage ./converter.nix { inherit (self) cursorgen; };
  cursors = self.callPackage ./cursors.nix { themes = null; };
})
