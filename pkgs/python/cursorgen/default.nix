{
  lib,
  python3Packages,
  fetchFromGitHub,
  imagemagick,
  ffmpeg,
  zlib,
}:
with python3Packages;
  buildPythonPackage rec {
    pname = "cursorgen";
    version = "1.0.0";

    src = fetchFromGitHub rec {
      owner = "ashuramaruzxc";
      repo = "${pname}";
      rev = "c095c30f5d322f4fdeb361fce9b22313b9bbf117";
      sha256 = "sha256-1c+oi6R2YKwHmMikmb4l7slw28i4XXFMicD8odOuEB4=";
    };

    doCheck = false;

    buildInputs = [ffmpeg imagemagick zlib];
    propagatedBuildInputs = [setuptools pillow numpy];

    meta = with lib; {
      description = "Cursorgen is a fork of win2xcur that aims to preserve the image quality of the cursor ";
      homepage = "https://github.com/ashuramaruzxc/cursorgen";
      changelog = "https://github.com/ashuramaruzxc/cursorgen/releases/tag/v${version}";
      license = licenses.gpl3Plus;
      maintainers = with maintainers; [ashuramaruzxc];
    };
  }
