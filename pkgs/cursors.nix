{
  lib,
  stdenvNoCC,
  symlinkJoin,
  runCommand,
  writeText,
  cacert,
  converter,
  themes ? null,
}:
let
  catalog = lib.trivial.importJSON ../CursorConverter/config/cursor_data.json;
  manifest = lib.trivial.importJSON ../CursorConverter/config/asset_sources.json;
  complete = lib.attrsets.filterAttrs (_: theme: theme.missing_roles == [ ]) catalog;
  selected = if themes == null then builtins.attrNames complete else lib.lists.unique themes;
  requiredArchives = lib.lists.unique (
    lib.lists.concatMap (
      name:
      map (asset: asset.archive) (
        builtins.attrValues manifest.themes.${name}
        ++ builtins.attrValues (manifest.notices.${catalog.${name}.group} or { })
      )
    ) selected
  );
  # Order the archives because builder sandboxes cannot share the Python queue
  archiveQueue = builtins.listToAttrs (
    lib.lists.zipListsWith lib.attrsets.nameValuePair requiredArchives ([ null ] ++ requiredArchives)
  );
  archives = lib.attrsets.mapAttrs (
    name: archive:
    let
      description = writeText "anime-cursors-${name}-source.json" (builtins.toJSON archive);
      previous = archiveQueue.${name} or null;
    in
    runCommand "anime-cursors-${name}.zip"
      {
        nativeBuildInputs = [ converter.pythonModule ];
        SSL_CERT_FILE = "${cacert}/etc/ssl/certs/ca-bundle.crt";
        outputHashMode = "flat";
        outputHashAlgo = "sha256";
        outputHash = archive.sha256;
        impureEnvVars = lib.fetchers.proxyImpureEnvVars;
        preferLocalBuild = true;
      }
      ''
        ${lib.strings.optionalString (previous != null) "test -f ${archives.${previous}}"}
        python ${../CursorConverter/downloads.py} ${description} "$out"
      ''
  ) manifest.archives;
  pythonEnv = converter.pythonModule.withPackages (_: [ converter ]);
  meta = {
    description = "Animated character cursor themes";
    homepage = "https://github.com/ashuramaruzxc/anime-cursors";
    maintainers = [ lib.maintainers.ashuramaruzxc ];
    license = lib.licenses.cc-by-nc-sa-40;
    platforms = lib.systems.doubles.linux;
  };
  source = lib.fileset.toSource {
    root = ../.;
    fileset = lib.fileset.unions [
      ../process_cursors.py
      ../LICENSE
    ];
  };
  variants = lib.attrsets.mapAttrs (
    name: theme:
    let
      notices = manifest.notices.${theme.group} or { };
      archiveNames = lib.lists.unique (
        map (asset: asset.archive) (
          builtins.attrValues manifest.themes.${name} ++ builtins.attrValues notices
        )
      );
      archiveMap = writeText "${name}-archives.json" (
        builtins.toJSON (lib.attrsets.genAttrs archiveNames (key: archives.${key}))
      );
    in
    stdenvNoCC.mkDerivation {
      pname = "anime-cursors-${name}";
      version = "8";
      src = source;
      strictDeps = true;
      nativeBuildInputs = [ pythonEnv ];
      buildPhase = ''
        runHook preBuild
        export ANIME_CURSOR_ASSET_ROOT="$PWD/assets/animated"
        python -m CursorConverter.assets --theme ${lib.strings.escapeShellArg name} \
          --archive-map ${archiveMap}
        python process_cursors.py --theme ${lib.strings.escapeShellArg name} \
          --jobs "$NIX_BUILD_CORES" --format directory --output themes
        runHook postBuild
      '';
      installPhase = ''
        runHook preInstall
        mkdir -p "$out/share/icons"
        cp -a themes/. "$out/share/icons/"
        mkdir -p "$out/share/doc/anime-cursors/${name}"
        cp LICENSE "$out/share/doc/anime-cursors/${name}/LICENSE"
        cp themes/anime-${lib.strings.escapeShellArg name}/ATTRIBUTION.txt \
          "$out/share/doc/anime-cursors/${name}/ATTRIBUTION.txt"
        ${lib.strings.optionalString (notices != { }) ''
          cp -R ${lib.strings.escapeShellArg "assets/notices/${theme.group}/."} \
            "$out/share/doc/anime-cursors/${name}/"
        ''}
        runHook postInstall
      '';
      passthru.themeName = "anime-${name}";
      meta = meta // {
        description = "${theme.name} animated cursor theme";
      };
    }
  ) complete;
in
assert lib.asserts.assertMsg (selected != [ ]) "Select at least one cursor theme";
lib.trivial.checkListOfEnum "anime-cursors: themes" (builtins.attrNames complete) selected
  symlinkJoin
  {
    pname = "anime-cursors";
    version = "8";
    paths = map (name: variants.${name}) selected;
    passthru = variants // {
      inherit variants;
      themes = selected;
      availableThemes = builtins.attrNames complete;
    };
    inherit meta;
  }
