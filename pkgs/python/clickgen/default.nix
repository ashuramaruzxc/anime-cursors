{
  lib,
  python3Packages,
  imagemagick,
}:
with python3Packages;
  buildPythonApplication rec {
    pname = "clickgen";
    version = "2.2.0";
    format = "wheel";
    src = fetchPypi rec {
      inherit pname version format;
      sha256 = "sha256-ls/+iAJ/999W53FIrA5HLKg8KZeQhqKlDow2R1w4OT8=";
      dist = python;
      python = "py3";
    };

    doCheck = false;

    buildInputs = [imagemagick];
    propagatedBuildInputs = [wand pillow pyyaml attrs toml numpy];

    meta = with lib; {
      description = "Tool that converts cursors from Windows format to Xcursor format";
      homepage = "https://github.com/quantum5/win2xcur";
      changelog = "https://github.com/quantum5/win2xcur/releases/tag/v${version}";
      license = licenses.gpl3Plus;
      maintainers = with maintainers; [ashuramaruzxc];
    };
  }
