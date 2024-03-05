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
    pname = "win2xcur";
    version = "0.1.2";

    src = fetchFromGitHub rec {
      owner = "ashuramaruzxc";
      repo = "${pname}";
      rev = "743ca3341ce2b08895bcd05eca503a6b4343c9b3";
      sha256 = "sha256-QItkTWMtWtcHHiOjfTLwRCPtnwnrpa2XR1eREtP2tCQ=";
    };

    doCheck = false;

    buildInputs = [ffmpeg imagemagick zlib];
    propagatedBuildInputs = [setuptools pillow numpy];

    meta = with lib; {
      description = "Tool that converts cursors from Windows format to Xcursor format";
      homepage = "https://github.com/quantum5/win2xcur";
      changelog = "https://github.com/quantum5/win2xcur/releases/tag/v${version}";
      license = licenses.gpl3Plus;
      maintainers = with maintainers; [ashuramaruzxc];
    };
  }
