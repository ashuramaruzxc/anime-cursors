{
  lib,
  stdenvNoCC,
  fetchFromGitHub,
  python3,
  cursorgen,
  unzip,
}:

let
  variants = [
    "aya"
    "cirno"
    "flandre"
    "hina"
    "iku"
    "junko"
    "kaguya"
    "keine"
    "keine_hakutaku"
    "koishi"
    "marisa"
    "mokou"
    "momiji"
    "nitori"
    "patchouli"
    "reimu"
    "reisen"
    "remilia"
    "rumia"
    "sakuya"
    "sanae"
    "satori"
    "suwako"
    "tewi"
    "utsuho"
    "wriggle"
    "youmu"
    "yukari_pcb"
    "yukari_swr"
    "yuugi"
    "yuuka"
  ];

  pythonEnv = python3.withPackages (
    ps: with ps; [
      pillow
      tqdm
    ]
  );
in
stdenvNoCC.mkDerivation rec {
  pname = "anime-cursors";
  version = "7";

  src = fetchFromGitHub {
    owner = "ashuramaruzxc";
    repo = "anime-cursors";
    rev = "master";
    hash = "sha256-KN/GPz79FthyDfZoGGdPYjNyiQMGMxVxC4UzQRdNP44=";
  };

  nativeBuildInputs = [
    pythonEnv
    cursorgen
    unzip
  ];

  outputs = variants ++ [ "out" ];

  outputsToInstall = [ ];

  buildPhase = ''
    runHook preBuild
    patchShebangs .
    mkdir -p dist
    export PYTHONPATH=$PYTHONPATH:$PWD
    python process_cursors.py
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall

    for output in $(getAllOutputNames); do
      if [ "$output" != "out" ]; then
        local outputDir="''${!output}"
        local iconsDir="$outputDir/share/icons"
        
        mkdir -p "$iconsDir"
        
        local displayName
        case "$output" in
          keine_hakutaku)
            displayName="Keine_Hakutaku"
            ;;
          yukari_pcb)
            displayName="Yukari PCB"
            ;;
          yukari_swr)
            displayName="Yukari SWR"
            ;;
          *)
            # Capitalize first letter
            displayName="''${output^}"
            ;;
        esac
        
        if [ -f "dist/$displayName.zip" ]; then
          unzip "dist/$displayName.zip" -d "$iconsDir"
        else
          echo "Warning: dist/$displayName.zip not found"
        fi
      fi
    done

    mkdir -p "$out/share/icons"
    if [ -f "dist/Remilia.zip" ]; then
      unzip "dist/Remilia.zip" -d "$out/share/icons"
    fi

    runHook postInstall
  '';

  meta = {
    description = "Touhou Project character cursor themes";
    homepage = "https://github.com/ashuramaruzxc/anime-cursors";
    license = lib.licenses.cc-by-nc-sa-40;
    maintainers = with lib.maintainers; [ ashuramaruzxc ];
  };
}
