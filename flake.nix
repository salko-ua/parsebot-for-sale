{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        inherit (self) outputs;
        inherit (pkgs) lib;

        pkgs = import nixpkgs {
          inherit system;
          overlays = [ ];
        };
      in
      {
        inherit pkgs;

        devShell = pkgs.mkShell {
          packages =
            with pkgs;
            [
              postgresql
              python3
              python3Packages.sqlalchemy
              python3Packages.pytest
              python3Packages.aiohttp
              python3Packages.requests
              python3Packages.aiogram
              python3Packages.sentry-sdk
              python3Packages.apscheduler
              python3Packages.beautifulsoup4
              python3Packages.aiosqlite
              python3Packages.dateutil
            ] ++ python3Packages.fastapi.optional-dependencies.standard;
          PYTHONPATH = ".";
        };

      }
    );
}
