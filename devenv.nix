{
  pkgs,
  lib,
  ...
}:
{
  # https://devenv.sh/packages/
  packages =
    with pkgs;
    [
      git
      just
      just-lsp
      python314Packages.tkinter
      ruff
    ]
    ++ lib.optionals (stdenv.hostPlatform.isLinux) [
      # Utility for I2C devices.
      # https://archive.kernel.org/oldwiki/i2c.wiki.kernel.org/index.php/I2C_Tools.html
      i2c-tools
      # Low-level C and Python libraries for manipulating GPIO.
      # https://github.com/joan2937/lg
      python314Packages.lgpio
    ];

  # https://devenv.sh/languages/
  languages = {
    python = {
      enable = true;
      venv.enable = true;
      uv = {
        enable = true;
        sync.enable = true;
      };
    };
  };

  # https://devenv.sh/scripts/
  scripts.version.exec = ''
    python3 --version
    uv --version
  '';

  # https://devenv.sh/basics/
  enterShell = ''
    version
  '';
}
