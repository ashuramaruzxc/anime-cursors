{
  lib,
  buildPythonPackage,
  hatchling,
  uv-build,
  numpy,
  pillow,
  opencv-python-headless,
  rich,
  python,
  src,
}:
let
  project = lib.trivial.importTOML "${src}/pyproject.toml";
  modern = project.build-system.build-backend == "uv_build";
in
buildPythonPackage {
  pname = "cursorgen";
  version = project.project.version;
  disabled = modern && lib.strings.versionOlder python.pythonVersion "3.14";
  pyproject = true;
  inherit src;

  # Keep the published Pillow version usable while the updated fork is local
  build-system = if modern then [ uv-build ] else [ hatchling ];
  dependencies = [
    numpy
  ]
  ++ (
    if modern then
      [
        opencv-python-headless
        rich
      ]
    else
      [ pillow ]
  );

  pythonImportsCheck = [
    "cursorgen"
    "cursorgen.parser"
    "cursorgen.writer"
  ];

  meta = {
    description = "Convert Windows cursors to X11 without losing image quality";
    homepage = "https://github.com/meanvoid/cursorgen";
    maintainers = [ lib.maintainers.ashuramaruzxc ];
    license = lib.licenses.gpl3Plus;
    mainProgram = "cursorgen";
  };
}
