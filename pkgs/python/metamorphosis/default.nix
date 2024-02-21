{
  lib,
  python3Packages,
  fetchFromGitHub,
  imagemagick,
}:
with lib;
  stdenv.mkDerivation rec {
    pname = "Metamorphosis";
    version = "V (Reborn)";
    src = fetchFromGitHub rec {
      owner = "SystemRage";
      repo = pname;
      rev = "53f4638";
      sha256 = "sha256-7NBpLn/XXXxh/O/9zO/pEHd828JGqSt83hSQIkqeRYo=";
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
