{
  lib,
  python3,
  fetchFromGitHub,
}:

python3.pkgs.buildPythonApplication rec {
  pname = "asyncache";
  version = "unstable-2023-12-22";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "hephex";
    repo = "asyncache";
    rev = "35c7966101f3b0c61c9254a03fb02cca6a9b2f50";
    hash = "sha256-qNPAgVBj3w9sgymM9pw1QW56bhf2zc1cpe3hBUaAApc=";
  };

  build-system = [
    python3.pkgs.poetry-core
  ];

  dependencies = with python3.pkgs; [
    cachetools
  ];

  pythonImportsCheck = [
    "asyncache"
  ];

  meta = {
    description = "Helpers to use cachetools with async functions";
    homepage = "git@github.com:hephex/asyncache.git";
    changelog = "https://github.com/hephex/asyncache/blob/${src.rev}/CHANGELOG.rst";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ ];
    mainProgram = "asyncache";
  };
}
