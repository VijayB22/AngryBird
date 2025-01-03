{ pkgs }:
pkgs.mkShell {
  buildInputs = [ pkgs.python3 pkgs.python3Packages.pip ];
}
