"""
Configuration loader for the String Search Server.

This module reads parameters from a configuration file (e.g., server_config.conf)
and exposes them as attributes for other modules to use.

Supported parameters include:

Host and port information
File path for data loading
Option to reread data on each query
SSL and authentication settings
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    Loads and manages the server configuration.

    This class reads configuration options from a plain text file and stores them
    as attributes. It supports both standard and SSL-enabled setups.

    Example configuration file:
        host=127.0.0.1
        port=44445
        linuxpath=/data/texts/source.txt
        REREAD_ON_QUERY=True
        SSL_ENABLED=True
        CERTFILE=certs/server.crt
        KEYFILE=certs/server.key
        CAFILE=certs/ca.crt
        PSK=mysecretkey

    Attributes:
        host (str): The hostname or IP address where the server will listen.
        port (int): The port number for the server connection.
        linuxpath (str): Path to the text file used for string search operations.
        reread_on_query (bool): Whether to reload the file content for every query.
        ssl_enabled (bool): Enables SSL/TLS encryption if True.
        certfile (Optional[str]): Path to the SSL certificate file.
        keyfile (Optional[str]): Path to the SSL private key file.
        cafile (Optional[str]): Path to the certificate authority (CA) file.
        psk (Optional[str]): Optional pre-shared key for additional authentication.
    """

    def __init__(self, config_file: str):
        self.config_file = Path(config_file)
        self.host: str = "0.0.0.0"
        self.port: int = 44445
        self.linuxpath: str = "."  # Fixed: changed from file_path to linuxpath
        self.reread_on_query: bool = False
        self.ssl_enabled: bool = False
        self.certfile: Optional[str] = None
        self.keyfile: Optional[str] = None
        self.cafile: Optional[str] = None
        self.psk: Optional[str] = None

        self._load_config()

    def _load_config(self) -> None:
        """
        Internal method that reads configuration parameters from the given file.

        Ignores comments (lines starting with '#') and empty lines.
        """
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                line_number = 0
                for line in f:
                    line_number += 1
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue  # Skip comments or empty lines

                    if "=" not in line:
                        logger.warning(
                            f"Line {line_number}: Invalid format (missing '='). Skipping: {line}"
                        )
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    try:
                        if (
                            key == "linuxpath" or key == "file_path"
                        ):  # Fixed: support both linuxpath and file_path
                            self.linuxpath = value
                            logger.debug(f"Configuration: Data file path set to '{value}'")
                        elif key == "host":
                            self.host = value
                            logger.debug(f"Configuration: Host set to '{value}'")
                        elif key == "port":
                            try:
                                port = int(value)
                                if not (1 <= port <= 65535):
                                    error_msg = f"Invalid port '{value}'. Port {port} out of valid range (1-65535)"
                                    logger.error(f"Line {line_number}: {error_msg}")
                                    raise ValueError(error_msg)
                                self.port = port
                                logger.debug(f"Configuration: Port set to {self.port}")
                            except ValueError as e:
                                if "out of valid range" in str(e):
                                    raise  # Re-raise our validation error
                                else:
                                    error_msg = f"Line {line_number}: Invalid port '{value}'. Must be a number between 1-65535"
                                    logger.error(error_msg)
                                    raise ValueError(error_msg)
                        elif key == "reread_on_query":
                            self.reread_on_query = value.lower() in ("true", "1", "yes")
                            mode = "dynamic" if self.reread_on_query else "static"
                            logger.debug(
                                f"Configuration: File mode set to '{mode}' "
                                f"(reread_on_query={self.reread_on_query})"
                            )
                        elif key == "ssl_enabled":
                            self.ssl_enabled = value.lower() in ("true", "1", "yes")
                            status = "enabled" if self.ssl_enabled else "disabled"
                            logger.debug(f"Configuration: SSL/TLS {status}")
                        elif key == "certfile" or key == "ssl_certfile":
                            self.certfile = value
                            logger.debug(f"Configuration: Certificate file set to '{value}'")
                        elif key == "keyfile" or key == "ssl_keyfile":
                            self.keyfile = value
                            logger.debug(f"Configuration: Key file set to '{value}'")
                        elif key == "cafile" or key == "ssl_cafile":
                            self.cafile = value
                            logger.debug(f"Configuration: CA file set to '{value}'")
                        elif key == "psk":
                            self.psk = value
                            if value:
                                logger.debug("Configuration: PSK authentication configured")
                            else:
                                logger.warning("Configuration: Empty PSK value provided")
                        else:
                            logger.warning(
                                f"Line {line_number}: Unknown configuration key '{key}'. Skipping."
                            )
                    except ValueError as e:
                        # Re-raise ValueError for critical config errors
                        error_msg = f"Line {line_number}: Error processing '{line}': {str(e)}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    except Exception as e:
                        logger.error(f"Line {line_number}: Error processing '{key}={value}': {e}")

            # Validate required fields after parsing
            if not self.linuxpath or self.linuxpath == ".":
                raise ValueError(
                    "Required configuration field 'linuxpath' (or 'file_path') is missing or invalid"
                )

            logger.info(f"Configuration loaded successfully from {self.config_file}")

        except (ValueError, FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            # Re-raise these specific exceptions directly
            logger.error(f"Failed to load configuration from {self.config_file}: {e}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error reading configuration file {self.config_file}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def __repr__(self) -> str:
        """Returns a readable string representation of the configuration."""
        return (
            f"Config(host='{self.host}', port={self.port}, linuxpath='{self.linuxpath}', "
            f"reread_on_query={self.reread_on_query}, ssl_enabled={self.ssl_enabled}, "
            f"certfile={self.certfile}, keyfile={self.keyfile}, cafile={self.cafile}, "
            f"psk={'***' if self.psk else None})"
        )


# Example usage
if __name__ == "__main__":
    try:
        config = Config("config/server_config.conf")
        print(config)
    except Exception as e:
        print(f"Failed to load configuration: {e}")
