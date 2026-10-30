{
  lib,
  buildPythonPackage,
  hatchling,
  numpy,
  opencv-python-headless,
  rich,
  typing-extensions,
  src,
}:
let
  project = lib.trivial.importTOML "${src}/pyproject.toml";
in
buildPythonPackage {
  pname = "cursorgen";
  version = project.project.version;
  pyproject = true;
  inherit src;

  build-system = [ hatchling ];
  dependencies = [
    numpy
    opencv-python-headless
    rich
    typing-extensions
  ];

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
