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
  version = "8";
  src = fetchFromGitHub {
    owner = "ashuramaruzxc";
    repo = "anime-cursors";
    rev = "v${version}";
    hash = "sha256-7XWQ7ADF3Zk34xDuP9OrUVB4bup0VPFQ9Wv9xUmOvCI=";
  };
  nativeBuildInputs = [
    pythonEnv
    cursorgen
    unzip
  ];

  # Remove the multiple outputs and outputsToInstall
  # outputs = variants ++ [ "out" ];
  # outputsToInstall = [ ];

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

    mkdir -p $out/share/icons

    for variant in ${toString variants}; do
      local displayName
      case "$variant" in
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
          displayName="''${variant^}"
          ;;
      esac
      
      if [ -f "dist/$displayName.zip" ]; then
        mkdir -p "$out/share/icons/touhou-$variant"
        unzip "dist/$displayName.zip" -d "$out/share/icons/touhou-$variant"
      else
        echo "Warning: dist/$displayName.zip not found"
      fi
    done

    runHook postInstall
  '';

  meta = {
    description = "Touhou Project character cursor themes";
    homepage = "https://github.com/ashuramaruzxc/anime-cursors";
    license = lib.licenses.cc-by-nc-sa-40;
    maintainers = with lib.maintainers; [ ashuramaruzxc ];
  };
}
