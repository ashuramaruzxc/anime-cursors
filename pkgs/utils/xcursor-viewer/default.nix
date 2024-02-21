{
  lib,
  stdenv,
  fetchFromGitHub,
  cmake,
  qtbase,
  wrapQtAppsHook,
}:
with lib;
  stdenv.mkDerivation rec {
    pname = "xcursor-viewer";
    version = "6b8a95a";

    src = fetchFromGitHub {
      owner = "drizt";
      repo = pname;
      rev = "${version}";
      sha256 = "sha256-65oL1zVNFhKM2ePNvWdSyUIEkHGktNFP5k0/oI+S2j0=";
    };

    buildInputs = [qtbase];
    nativeBuildInputs = [cmake wrapQtAppsHook];

    CMAKE_PREFIX_PATH = [qtbase];

    meta = {
      description = "A simple XCursor viewer";
      homepage = "https://github.com/drizt/xcursor-viewer";
      license = licenses.gpl3;
      maintainers = with maintainers; [ashuramaruzxc];
    };
  }
