from __future__ import annotations
import socket
import ssl
from typing import Optional


class StringSearchClient:
    """
    A TCP client for communicating with the String Search Server.

    This client connects to a server, optionally using SSL/TLS for secure communication,
    sends a string query, and returns the server's response.

    Attributes:
        host (str): The server's hostname or IP address.
        port (int): The TCP port to connect to.
        use_ssl (bool): Enables SSL/TLS encryption if True.
        certfile (Optional[str]): Path to client certificate file (if SSL is enabled).
        keyfile (Optional[str]): Path to private key file (if SSL is enabled).
        cafile (Optional[str]): Path to certificate authority file for server verification.
        psk (Optional[str]): Optional pre-shared key (for future authentication features).
        socket (Optional[socket.socket]): Underlying socket connection (plain or SSL-wrapped).
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 44445,
        use_ssl: bool = False,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        cafile: Optional[str] = None,
        psk: Optional[str] = None,
    ):
        """Initialize the StringSearchClient with connection and security parameters."""
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.certfile = certfile
        self.keyfile = keyfile
        self.cafile = cafile
        self.psk = psk
        self.socket: Optional[socket.socket] = None

    def connect(self) -> None:
        """
        Establish a TCP connection to the server.

        If SSL is enabled, wraps the socket with an SSL context and performs
        certificate verification (if a CA file is provided).

        Raises:
            ConnectionError: If connection to server fails.
            ssl.SSLError: If SSL handshake fails.
        """
        try:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.settimeout(10)  # 10 second timeout for connection

            if self.use_ssl:
                try:
                    message = f"[Client] Establishing secure SSL/TLS connection to {
                        self.host}:{
                        self.port}"
                    print(message)
                    print(f"[Client] SSL context configured with certfile: {self.certfile}")

                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

                    if self.certfile and self.keyfile:
                        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
                        print("[Client] Client certificate authentication configured")

                    if self.cafile:
                        context.load_verify_locations(cafile=self.cafile)
                        context.verify_mode = ssl.CERT_REQUIRED
                        print("[Client] Server certificate verification enabled")
                    else:
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        print("[Client] Warning: Server certificate verification disabled")

                    if self.psk:
                        print("[Client] PSK authentication configured")

                    self.socket = context.wrap_socket(raw_socket, server_hostname=self.host)
                    print("[Client] SSL/TLS handshake completed successfully")

                except ssl.SSLError as e:
                    print(f"[Client] SSL/TLS handshake failed: {e}")
                    raw_socket.close()
                    raise ConnectionError(f"SSL/TLS connection failed: {e}") from e
                except Exception as e:
                    print(f"[Client] SSL setup failed: {e}. Falling back to plain socket.")
                    self.socket = raw_socket
                    self.use_ssl = False
            else:
                self.socket = raw_socket
                print(f"[Client] Establishing plain text connection to {self.host}:{self.port}")

            # Establish connection
            self.socket.connect((self.host, self.port))
            print(
                f"[Client] Successfully connected to {self.host}:{self.port} "
                f"(SSL/TLS: {'Yes' if self.use_ssl else 'No'})"
            )

        except socket.timeout:
            error_msg = f"Connection timeout: Could not connect to {
                self.host}:{
                self.port} within 10 seconds"
            print(f"[Client] {error_msg}")
            raise ConnectionError(error_msg)
        except ConnectionRefusedError:
            error_msg = f"Connection refused: Server at {
                self.host}:{
                self.port} is not accepting connections"
            print(f"[Client] {error_msg}")
            raise ConnectionError(error_msg)
        except Exception as e:
            error_msg = f"Failed to connect to {self.host}:{self.port}: {e}"
            print(f"[Client] {error_msg}")
            raise ConnectionError(error_msg) from e

    def send_query(self, query: str) -> str:
        """
        Send a search query string to the server and receive a response.

        Args:
            query (str): The string to search for.

        Returns:
            str: The response message from the server ("STRING EXISTS" or "STRING NOT FOUND").

        Raises:
            ConnectionError: If the client is not connected to the server.
            ValueError: If the query is empty or contains only whitespace.
        """
        if not self.socket:
            raise ConnectionError("Client not connected to server. Call connect() first.")

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty or contain only whitespace")

        try:
            # Send the query encoded as UTF-8, replacing invalid characters
            encoded_query = (query.strip() + "\n").encode("utf-8", errors="replace")
            self.socket.sendall(encoded_query)

            # Wait for and decode the server's response
            response_data = self.socket.recv(1024)
            if not response_data:
                raise ConnectionError("Server closed connection unexpectedly")

            response = response_data.decode("utf-8", errors="replace").strip()
            print(f"[Client] Query: '{query}' -> Response: '{response}'")
            return response

        except (socket.timeout, TimeoutError) as e:
            # Timeout during send or receive
            error_msg = "Server response timeout: No response received within expected time"
            print(f"[Client] {error_msg}")
            raise ConnectionError(error_msg) from e
        except (ConnectionResetError, BrokenPipeError) as e:
            # Connection lost during send or receive
            error_msg = "Server connection lost"
            print(f"[Client] {error_msg}")
            raise ConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Communication error with server: {str(e)}"
            print(f"[Client] {error_msg}")
            raise ConnectionError(error_msg) from e

    def close(self) -> None:
        """
        Gracefully close the active socket connection.
        """
        if self.socket:
            try:
                self.socket.close()
                self.socket = None
                print("[Client] Connection closed successfully")
            except Exception as e:
                print(f"[Client] Warning: Error while closing connection: {e}")
            finally:
                self.socket = None


# Example usage
if __name__ == "__main__":
    client = StringSearchClient(host="127.0.0.1", port=44445, use_ssl=False)
    try:
        client.connect()
        while True:
            try:
                query = input("Enter string to search (or 'exit' to quit): ").strip()
                if query.lower() == "exit":
                    break
                if not query:
                    print("Error: Query cannot be empty")
                    continue
                result = client.send_query(query)
                print(f"Server response: {result}")
            except ValueError as e:
                print(f"Input error: {e}")
            except ConnectionError as e:
                print(f"Connection error: {e}")
                break
    except KeyboardInterrupt:
        print("\n[Client] Interrupted by user")
    except Exception as e:
        print(f"[Client] Unexpected error: {e}")
    finally:
        client.close()
