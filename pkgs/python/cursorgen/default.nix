{
  lib,
  python3Packages,
}:
with python3Packages;
  buildPythonPackage rec {
    pname = "cursorgen";
    version = "0.1.2";
    format = "wheel";
    src = fetchPypi rec {
      inherit pname version format;
      sha256 = "sha256-/jrhgApJTRKuMCE33Q7SGGy4oXPARzWJSXFJWKO3N5o=";
      dist = python;
      python = "py3";
    };

    doCheck = false;

    propagatedBuildInputs = [pillow numpy];

    meta = with lib; {
      description = " cursorgen is a fork of win2xcur that aims to preserve the image quality of the cursor ";
      homepage = "https://github.com/ashuramaruzxc/cursorgen";
      changelog = "https://github.com/ashuramaruzxc/cursorgen/releases/tag/v${version}";
      license = licenses.gpl3Plus;
      maintainers = with maintainers; [ashuramaruzxc];
    };
  }
