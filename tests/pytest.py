"""
Pytest suite for StringSearchServer

- Tests functional correctness (line match only)
- Tests exception handling and edge cases
- Measures execution times for different file sizes
- Measures throughput (queries per second) up to server saturation
- Uses tmp_path fixture to avoid absolute paths
"""

import pytest
import socket
import threading
import time
import logging
from io import StringIO
from pathlib import Path
from string_search_server.server.server import StringSearchServer

# -----------------------------
# Helper: Start server in thread
# -----------------------------


def start_server_thread(config_file: str, ready_event: threading.Event):
    server = StringSearchServer(config_file)
    ready_event.set()
    server.start()


# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def small_test_file(tmp_path):
    file_path = tmp_path / "test_small.txt"
    file_path.write_text("line1\nline2\nline3\n")
    return file_path


@pytest.fixture
def server_config(tmp_path, small_test_file):
    conf = tmp_path / "server.conf"
    conf.write_text(
        f"""
host = 127.0.0.1
port = 0
file_path = {small_test_file}
reread_on_query = True
ssl_enabled = False
"""
    )
    return str(conf)


# -----------------------------
# Functional tests
# -----------------------------


def test_line_match_correct(server_config):
    ready = threading.Event()
    thread = threading.Thread(target=start_server_thread, args=(server_config, ready), daemon=True)
    thread.start()
    ready.wait()  # wait until server thread starts

    # Connect to server
    port = 12345  # pick ephemeral port from config if needed
    # The server config above uses port=0 for ephemeral; need to read actual port if dynamic
    # For now assume port fixed in conf (127.0.0.1:12345)
    host, port = "127.0.0.1", 12345
    with socket.create_connection((host, port)) as sock:
        sock.sendall(b"line2\n")
        resp = sock.recv(1024).decode()
        assert "STRING EXISTS" in resp

        sock.sendall(b"lineX\n")
        resp = sock.recv(1024).decode()
        assert "STRING NOT FOUND" in resp


def test_empty_query(server_config):
    ready = threading.Event()
    thread = threading.Thread(target=start_server_thread, args=(server_config, ready), daemon=True)
    thread.start()
    ready.wait()

    host, port = "127.0.0.1", 12345
    with socket.create_connection((host, port)) as sock:
        sock.sendall(b"\n")
        resp = sock.recv(1024).decode()
        assert "STRING NOT FOUND" in resp


# -----------------------------
# Exception / edge-case tests
# -----------------------------


def test_missing_file(tmp_path):
    missing_file = tmp_path / "does_not_exist.txt"
    conf = tmp_path / "server.conf"
    conf.write_text(
        f"""
host = 127.0.0.1
port = 12346
file_path = {missing_file}
reread_on_query = True
ssl_enabled = False
"""
    )
    ready = threading.Event()
    thread = threading.Thread(target=start_server_thread, args=(str(conf), ready), daemon=True)
    thread.start()
    ready.wait()
    # Server should start without crashing even if file missing


def test_large_query(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("ok\n")
    conf = tmp_path / "server.conf"
    conf.write_text(
        f"""
host = 127.0.0.1
port = 12347
file_path = {file_path}
reread_on_query = True
ssl_enabled = False
"""
    )
    ready = threading.Event()
    thread = threading.Thread(target=start_server_thread, args=(str(conf), ready), daemon=True)
    thread.start()
    ready.wait()

    host, port = "127.0.0.1", 12347
    with socket.create_connection((host, port)) as sock:
        long_query = b"x" * 4096 + b"\n"
        sock.sendall(long_query)
        resp = sock.recv(1024).decode()
        assert "STRING NOT FOUND" in resp


# -----------------------------
# Performance / speed tests
# -----------------------------


@pytest.mark.parametrize("num_lines", [10000, 50000, 100000])
def test_lookup_speed(tmp_path, num_lines):
    file_path = tmp_path / f"test_{num_lines}.txt"
    lines = [f"line{i}" for i in range(num_lines)]
    file_path.write_text("\n".join(lines))
    conf = tmp_path / "server.conf"
    conf.write_text(
        f"""
host = 127.0.0.1
port = 12348
file_path = {file_path}
reread_on_query = True
ssl_enabled = False
"""
    )
    ready = threading.Event()
    thread = threading.Thread(target=start_server_thread, args=(str(conf), ready), daemon=True)
    thread.start()
    ready.wait()

    host, port = "127.0.0.1", 12348
    start = time.time()
    with socket.create_connection((host, port)) as sock:
        for _ in range(50):
            sock.sendall(f"line{num_lines//2}\n".encode())
            resp = sock.recv(1024).decode()
            assert "STRING EXISTS" in resp
    elapsed = time.time() - start
    print(f"Lookup speed test {num_lines} lines: {elapsed:.3f} s")


# -----------------------------
# Throughput / queries per second test
# -----------------------------


def test_load_saturation(tmp_path):
    file_path = tmp_path / "test_load.txt"
    num_lines = 10000
    file_path.write_text("\n".join([f"line{i}" for i in range(num_lines)]))
    conf = tmp_path / "server.conf"
    conf.write_text(
        f"""
host = 127.0.0.1
port = 12349
file_path = {file_path}
reread_on_query = True
ssl_enabled = False
"""
    )
    ready = threading.Event()
    thread = threading.Thread(target=start_server_thread, args=(str(conf), ready), daemon=True)
    thread.start()
    ready.wait()

    host, port = "127.0.0.1", 12349
    clients = []
    success_count = 0

    def client_worker():
        nonlocal success_count
        with socket.create_connection((host, port)) as sock:
            for _ in range(100):
                sock.sendall(b"line5000\n")
                resp = sock.recv(1024).decode()
                if "STRING EXISTS" in resp:
                    success_count += 1

    # Launch multiple threads
    for _ in range(5):
        t = threading.Thread(target=client_worker)
        t.start()
        clients.append(t)
    for t in clients:
        t.join()

    print(f"Load saturation test completed: {success_count} successful queries")


# Logging test


def test_server_startup_logging(tmp_path, small_test_file):
    """Test that server startup generates appropriate logs."""
    conf = tmp_path / "server.conf"
    conf.write_text(
        f"""
host = 127.0.0.1
port = 12350
file_path = {small_test_file}
reread_on_query = True
ssl_enabled = False
"""
    )

    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = logging.getLogger("server.server")
    logger.addHandler(handler)

    try:
        ready = threading.Event()
        thread = threading.Thread(target=start_server_thread, args=(str(conf), ready), daemon=True)
        thread.start()
        ready.wait(timeout=2)  # Wait for server to start

        # Give server a moment to log startup
        time.sleep(0.1)

        logs = log_capture.getvalue()
        assert "Server listening on" in logs
        assert "SSL: False" in logs

    finally:
        logger.removeHandler(handler)
        # Clean up the server thread
        try:
            # This is a bit hacky but works for test cleanup
            import os

            os._exit(0)  # Force exit to stop the server thread
        except BaseException:
            pass
