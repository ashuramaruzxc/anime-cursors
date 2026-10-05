{
  lib,
  buildPythonPackage,
  uv-build,
  cursorgen,
  msgspec,
  numpy,
  pillow,
  platformdirs,
  rich,
  python,
}:
buildPythonPackage {
  pname = "anime-cursors";
  version = (lib.trivial.importTOML ../pyproject.toml).project.version;
  disabled = lib.strings.versionOlder python.pythonVersion "3.14";
  pyproject = true;
  src = lib.fileset.toSource {
    root = ../.;
    fileset = lib.fileset.unions [
      (lib.fileset.fileFilter (file: file.hasExt "py" || file.hasExt "json") ../CursorConverter)
      ../pyproject.toml
      ../README.md
      ../LICENSE
    ];
  };

  build-system = [ uv-build ];
  dependencies = [
    cursorgen
    msgspec
    numpy
    pillow
    platformdirs
    rich
  ];
  pythonImportsCheck = [
    "CursorConverter"
    "CursorConverter.assets"
    "CursorConverter.worker"
  ];

  meta = {
    description = "Convert animated Windows cursors into Xcursor themes";
    homepage = "https://github.com/ashuramaruzxc/anime-cursors";
    maintainers = [ lib.maintainers.ashuramaruzxc ];
    license = lib.licenses.gpl3Plus;
    mainProgram = "CursorConverter";
  };
}
