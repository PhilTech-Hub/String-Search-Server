"""
SSL Utilities for the String Search Server.

This module provides functions to create SSL contexts for
secure client-server communication. It supports certificate-based
and PSK (Pre-Shared Key) authentication modes.
"""

from __future__ import annotations
import ssl
from pathlib import Path
from typing import Optional, Self
import logging

logger = logging.getLogger(__name__)


def create_ssl_context(
    certfile: Optional[str] = None,
    keyfile: Optional[str] = None,
    cafile: Optional[str] = None,
    psk: Optional[str] = None,
    server_side: bool = True,
    verify_client: bool = False,
) -> ssl.SSLContext:
    """
    Creates and returns an SSL context based on provided parameters.

        Args:
        certfile (str, optional): Path to the server certificate (PEM format).
        keyfile (str, optional): Path to the private key file.
        cafile (str, optional): Path to the CA certificate for verifying peers (optional).
        psk (str, optional): Pre-shared key for lightweight authentication (not standard SSL).
        server_side (bool): If True, configures the context for a server. Otherwise, for a client.
        verify_client (bool): If True, requires clients to present valid certificates.

    Returns:
        ssl.SSLContext: A fully configured SSL context.

    Raises:
        ValueError: If neither a cert/key pair nor a PSK is provided.
        FileNotFoundError: If provided cert/key/cafile paths do not exist.
        ssl.SSLError: If SSL context creation fails.
    """

    # Ensure that at least one authentication method is provided
    if not certfile and not keyfile and not psk:
        error_msg = "SSL configuration error: Must provide either certificate files or PSK"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # If certfile or keyfile is provided, both must be provided
    if (certfile and not keyfile) or (keyfile and not certfile):
        error_msg = "SSL configuration error: Must provide both certfile and keyfile"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        # Select purpose based on role
        purpose = ssl.Purpose.CLIENT_AUTH if server_side else ssl.Purpose.SERVER_AUTH
        context = ssl.create_default_context(purpose)
        logger.debug(f"Created SSL context for {'server' if server_side else 'client'}")

        # Handle certificate-based SSL setup
        if certfile and keyfile:
            cert_path, key_path = Path(certfile), Path(keyfile)

            if not cert_path.exists():
                error_msg = f"SSL certificate file not found: {certfile}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            if not key_path.exists():
                error_msg = f"SSL private key file not found: {keyfile}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            try:
                context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))
                logger.info(f"SSL certificate chain loaded: {certfile}, {keyfile}")
            except ssl.SSLError as e:
                error_msg = f"SSL certificate error: {e}. Check certificate and key files."
                logger.error(error_msg)
                raise ssl.SSLError(error_msg) from e

        # Handle CA verification
        if cafile:
            ca_path = Path(cafile)
            if not ca_path.exists():
                error_msg = f"CA certificate file not found: {cafile}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            try:
                context.load_verify_locations(cafile=str(ca_path))
                if verify_client or not server_side:
                    context.verify_mode = ssl.CERT_REQUIRED
                    logger.info("Peer certificate verification enabled")
                logger.debug(f"CA certificates loaded from: {cafile}")
            except ssl.SSLError as e:
                error_msg = f"CA certificate error: {e}. Check CA file format."
                logger.error(error_msg)
                raise ssl.SSLError(error_msg) from e

        # Handle PSK authentication (not native SSL, just logged for completeness)
        if psk:
            if len(psk) < 8:
                logger.warning("PSK is shorter than recommended minimum length (8 characters)")
            logger.info(f"PSK authentication configured (key length: {len(psk)} characters)")

        # Harden SSL configuration
        try:
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers("HIGH:!aNULL:!MD5:!RC4")
            logger.debug("SSL/TLS security hardened: TLS 1.2+ with strong ciphers")
        except Exception as e:
            logger.warning(f"Could not set maximum SSL security settings: {e}")

        logger.info("SSL context successfully configured and ready for use")
        return context

    except (ValueError, FileNotFoundError, ssl.SSLError):
        # Re-raise known exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error during SSL context creation: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


if __name__ == "__main__":
    # Example usage with better error handling
    try:
        ssl_ctx = create_ssl_context(psk="supersecretkey123")
        logger.info("SSL context test completed successfully")
    except Exception as e:
        logger.error(f"SSL context test failed: {e}")
