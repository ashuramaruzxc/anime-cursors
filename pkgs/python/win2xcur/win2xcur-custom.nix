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
      rev = "51633b9f14739e9be347e0afb3f1a7809b53e242";
      sha256 = "sha256-Tok+9UPLjohr9Qh+Lc8zlx14uMJhF7dTj9XYhEcYkuI=";
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
