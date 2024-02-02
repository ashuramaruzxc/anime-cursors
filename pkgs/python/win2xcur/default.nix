{
  lib,
  python3Packages,
  imagemagick,
}:
with python3Packages;
  buildPythonApplication rec {
    pname = "win2xcur";
    version = "0.1.2";
    format = "wheel";
    src = fetchPypi rec {
      inherit pname version format;
      sha256 = "sha256-utcBq5xAMUeQkdgQkLYO+oXQj/Woj2jlQQqcqkahxbo=";
      dist = python;
      python = "py3";
    };
    
    doCheck = false;

    buildInputs = [imagemagick];
    propagatedBuildInputs = [wand numpy];

    meta = with lib; {
      description = "Tool that converts cursors from Windows format to Xcursor format";
      homepage = "https://github.com/quantum5/win2xcur";
      changelog = "https://github.com/quantum5/win2xcur/releases/tag/v${version}";
      license = licenses.gpl3Plus;
      maintainers = with maintainers; [ashuramaruzxc];
    };
  }
