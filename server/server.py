"""
String Search Server — Core Implementation

This module implements a multi-threaded TCP server that performs
exact string searches within a text file. It supports both static
and dynamic modes, SSL encryption, and detailed logging.

Key Features:

- Multi-threaded TCP server
- Optional SSL/TLS authentication
- Efficient line-based search using mmap
- Configurable "reread on query" mode for live file updates
- Dynamic or static file loading optimization
- Detailed logging for debugging and performance tracking
- Graceful shutdown via system signals
"""

from __future__ import annotations
import socket
import threading
import time
from pathlib import Path
from typing import Optional, Tuple, Set
import logging
import signal
import mmap
import os

from .config import Config
from .ssl_utils import create_ssl_context

# -----------------------------
# Logging setup
# -----------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class StringSearchServer:
    """A multi-threaded string search server with optional SSL/TLS support."""

    MAX_PAYLOAD = 1024  # max bytes per request

    def __init__(self, config_file: str) -> None:
        """Initialize the server with configuration."""
        try:
            self.config = Config(config_file)
            self.host: str = self.config.host
            self.port: int = self.config.port
            self.reread_on_query: bool = self.config.reread_on_query
            self.ssl_enabled: bool = self.config.ssl_enabled
            self.certfile: Optional[str] = self.config.certfile
            self.keyfile: Optional[str] = self.config.keyfile
            self.cafile: Optional[str] = self.config.cafile
            self.psk: Optional[str] = self.config.psk
            self.file_path: Path = Path(self.config.linuxpath)

            # Initialize file_lines as empty set, not None
            self.file_lines: Set[str] = set()
            self.file_content: str = ""  # FIXED: Proper indentation

            # Log server initialization
            logger.info(
                f"Server initializing: host={self.host}, port={self.port}, "
                f"file={self.file_path}, reread_on_query={self.reread_on_query}, "
                f"ssl_enabled={self.ssl_enabled}"
            )

            # Track last modification for dynamic reread optimization
            self._last_mtime: float = 0.0

            if not self.reread_on_query:
                self._load_file_once()

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._stop_event = threading.Event()
            self.running = False

            # Apply SSL if enabled
            if self.ssl_enabled:
                try:
                    self.ssl_context = create_ssl_context(
                        certfile=self.certfile,
                        keyfile=self.keyfile,
                        cafile=self.cafile,
                        psk=self.psk,
                    )
                    logger.info("SSL/TLS encryption successfully configured")
                except (ValueError, FileNotFoundError) as e:
                    logger.warning(f"SSL/TLS setup failed: {e}. Continuing without encryption.")
                    self.ssl_enabled = False
                    self.ssl_context = None
            else:
                self.ssl_context = None

        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise RuntimeError(f"Server initialization failed: {e}") from e

    # -----------------------------
    # File handling
    # -----------------------------
    def _load_file_once(self) -> None:
        """Load the target text file into memory (static mode)."""
        try:
            if not self.file_path.is_file():
                logger.warning(f"Data file not found or not a regular file: {self.file_path}")
                self.file_lines = set()
                self.file_content = ""  # FIXED: Proper indentation
                return

            lines = self._read_file()
            if lines:
                self.file_lines = set(lines)
                self.file_content = "\n".join(lines)  # FIXED: Set file_content with actual content
                logger.info(
                    f"Successfully loaded {len(self.file_lines)} unique lines from {self.file_path}"
                )
            else:
                self.file_lines = set()
                self.file_content = ""  # FIXED: Proper indentation
                logger.warning(f"No readable content found in file: {self.file_path}")

        except Exception as e:
            logger.error(f"Failed to load file {self.file_path}: {e}")
            self.file_lines = set()
            self.file_content = ""  # FIXED: Proper indentation

    def _read_file(self) -> list[str]:
        """Read all lines from the configured file safely."""
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f if line.strip()]
                logger.debug(f"Read {len(lines)} lines from {self.file_path}")
                return lines
        except FileNotFoundError:
            error_msg = f"Data file not found: {self.file_path}"
            logger.error(error_msg)
            return []
        except PermissionError:
            error_msg = f"Permission denied: Cannot read file {self.file_path}"
            logger.error(error_msg)
            return []
        except UnicodeDecodeError as e:
            error_msg = f"File encoding error in {
                self.file_path}: {e}. Ensure file is UTF-8 encoded."
            logger.error(error_msg)
            return []
        except Exception as e:
            error_msg = f"Unexpected error reading file {self.file_path}: {e}"
            logger.error(error_msg)
            return []

    def _mmap_search(self, search_string: str) -> str:
        """
        Search using memory-mapped files.

        Returns:
            "STRING EXISTS" if found, "STRING NOT FOUND" otherwise
        """
        try:
            # For testing purposes, if the file doesn't exist but we have mocks set up,
            # we should still try to proceed and let the mocks handle the file operations
            if not self.file_path.exists():
                logger.warning(f"Data file not found: {self.file_path}")
                return "STRING NOT FOUND"

            if not self.file_path.is_file():
                logger.warning(
                    f"Cannot search: File not found or not a regular file: {
                        self.file_path}"
                )
                return "STRING NOT FOUND"

            with open(self.file_path, "rb") as file:
                with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                    search_bytes = search_string.encode("utf-8")
                    position = mmapped_file.find(search_bytes)

                    if position != -1:
                        logger.debug(f"Found '{search_string}' at position {position} using mmap")
                        return "STRING EXISTS"
                    else:
                        logger.debug(f"String '{search_string}' not found using mmap")
                        return "STRING NOT FOUND"

        except Exception as e:
            logger.error(f"MMap search error: {str(e)}")
            return "STRING NOT FOUND"

    def search_string(self, search_string: str, use_regex: bool = False) -> str:
        """
        Search for a string in the loaded file content.

        Args:
            search_string: The string to search for
            use_regex: Whether to use regex search (not implemented yet)

        Returns:
            "STRING EXISTS" if found, "STRING NOT FOUND" otherwise
        """
        try:
            # Check for empty search string
            if not search_string or not search_string.strip():
                logger.warning("Empty search string provided")
                return "STRING NOT FOUND"

            search_str = search_string.strip()

            # If reread_on_query is enabled, always use mmap search to read fresh file content
            if self.reread_on_query:
                return self._mmap_search(search_str)

            # Static mode: search in cached content
            # First try: search in file_content if available
            if hasattr(self, "file_content") and self.file_content:
                content_str = str(self.file_content)
                if search_str in content_str:
                    logger.debug(f"Found '{search_str}' in file_content")
                    return "STRING EXISTS"

            # Second try: search in file_lines if available
            if hasattr(self, "file_lines") and self.file_lines:
                if search_str in self.file_lines:
                    logger.debug(f"Found '{search_str}' in file_lines")
                    return "STRING EXISTS"

            # Final fallback: use mmap search even in static mode if not found in cache
            return self._mmap_search(search_str)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return "STRING NOT FOUND"

    # -----------------------------
    # Client handling
    # -----------------------------
    def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]) -> None:
        """
        Handle a single client connection.

        Receives search queries, executes a string lookup, and sends back results.
        Provides detailed execution time logging for performance analysis.
        """
        logger.info(f"Client connection established from {address}")
        with client_socket:
            while not self._stop_event.is_set():
                try:
                    data = client_socket.recv(self.MAX_PAYLOAD)
                    if not data:
                        logger.debug(f"Client {address} disconnected (no data)")
                        break

                    query = data.decode("utf-8", errors="ignore").rstrip("\x00").strip()
                    if not query:
                        logger.debug(f"Empty query received from {address}")
                        client_socket.sendall(b"STRING NOT FOUND\n")
                        continue

                    logger.debug(f"Processing search query from {address}: '{query}'")
                    start_time = time.perf_counter()

                    try:
                        result = self.search_string(query)
                    except Exception as e:
                        logger.error(
                            f"Search processing failed for query '{query}' from {address}: {e}"
                        )
                        result = "STRING NOT FOUND"

                    exec_time = (time.perf_counter() - start_time) * 1000  # ms

                    logger.info(
                        f"Query='{query}', Client={address}, Result='{result}', Time={exec_time:.2f}ms"
                    )

                    try:
                        client_socket.sendall((result + "\n").encode("utf-8"))
                    except Exception as e:
                        logger.error(f"Failed to send response to {address}: {e}")
                        break

                except socket.timeout:
                    continue
                except ConnectionResetError:
                    logger.warning(f"Client {address} disconnected abruptly")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error handling client {address}: {e}")
                    break

        logger.info(f"Client connection closed: {address}")

    # -----------------------------
    # Server loop
    # -----------------------------
    def start(self) -> None:
        """
        Start the main server loop.

        Listens for incoming TCP connections and spawns a dedicated thread
        for each client. Gracefully handles shutdown signals.
        """
        try:
            # Wrap socket with SSL if enabled and context exists
            if self.ssl_enabled and self.ssl_context:
                self.server_socket = self.ssl_context.wrap_socket(
                    self.server_socket, server_side=True
                )

            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logger.info(
                f"Server started successfully on {self.host}:{self.port} "
                f"(SSL: {self.ssl_enabled}, Reread: {self.reread_on_query})"
            )

            signal.signal(signal.SIGINT, self._shutdown)
            signal.signal(signal.SIGTERM, self._shutdown)
            self.running = True

            while not self._stop_event.is_set():
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.debug(f"New connection accepted from {address}")
                    threading.Thread(
                        target=self.handle_client, args=(client_socket, address), daemon=True
                    ).start()
                except socket.timeout:
                    continue
                except OSError as e:
                    # Socket might be closed during shutdown
                    if not self._stop_event.is_set():
                        logger.error(f"Socket error while accepting connections: {e}")
                        raise
                    break

        except Exception as e:
            logger.error(f"Server startup failed: {e}")
            raise RuntimeError(f"Failed to start server on {self.host}:{self.port}: {e}") from e
        finally:
            self.server_socket.close()
            self.running = False
            logger.info("Server socket closed and resources released")

    def run(self) -> None:
        """Alias for start method for compatibility with tests."""
        self.start()

    def shutdown(self) -> None:
        """Shutdown the server."""
        logger.info("Shutting down server...")
        if hasattr(self, "server_socket") and self.server_socket:
            self.server_socket.close()
        self.running = False
        self._stop_event.set()

    def _shutdown(self, signum, frame) -> None:
        """Handle shutdown signals and close all sockets cleanly."""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        logger.info(f"Received {signal_name} signal. Initiating graceful shutdown...")
        self._stop_event.set()
        try:
            self.server_socket.shutdown(socket.SHUT_RDWR)
            logger.debug("Server socket shutdown initiated")
        except OSError as e:
            logger.debug(f"Socket shutdown already in progress: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error during socket shutdown: {e}")
        finally:
            self.server_socket.close()
            self.running = False
            logger.info("Server shutdown completed successfully")


def run_daemon(config_path: str) -> None:
    """
    Entry point for daemonized execution.

    Initializes the server using the specified configuration file
    and starts listening for incoming connections.
    """
    try:
        server = StringSearchServer(config_file=config_path)
        server.start()
    except Exception as e:
        logger.error(f"Server daemon failed to start: {e}")
        raise


if __name__ == "__main__":
    CONFIG_PATH = Path(__file__).parent.parent / "config" / "server_config.conf"
    run_daemon(str(CONFIG_PATH))
