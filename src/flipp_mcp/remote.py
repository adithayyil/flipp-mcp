import os

from mcp.server.transport_security import TransportSecuritySettings

from .server import create_mcp


def main():
    mcp = create_mcp(
        host=os.environ.get("FLIPP_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLIPP_PORT", "8000")),
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        ),
    )
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
