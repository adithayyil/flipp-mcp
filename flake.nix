{
  description = "Flipp MCP server dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.uv
          pkgs.cloudflared
        ];

        shellHook = ''
          echo "[flipp-mcp] dev shell ready"
          echo "Set up the project:   uv sync"
          echo "Run stdio server:     uv run flipp-mcp"
          echo "Run remote server:    FLIPP_PORT=8001 uv run flipp-mcp-remote"
        '';
      };
    };
}
