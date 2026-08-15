import os

from .server import create_mcp


def main():
    mcp = create_mcp(
        host=os.environ.get("FLIPP_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLIPP_PORT", "8000")),
    )
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
