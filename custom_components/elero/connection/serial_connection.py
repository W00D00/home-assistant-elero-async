"""Asynchronous direct-serial (USB/COM) connection for Elero devices.

This module implements :class:`SerialConnection`, a concrete :class:`Connection`
that opens a serial port using ``serial_asyncio_fast`` and exposes the common
send/receive interface shared by the integration.

Configuration is provided via :class:`~custom_components.elero.connection.config.SerialConfig`:
    * ``device``: Port path/URL (e.g., ``/dev/ttyUSB0`` or ``COM3``)
    * ``baudrate``: Integer baud rate
    * ``bytesize``: Data bits (typically 8)
    * ``stopbits``: Stop bits (e.g., 1)
    * ``parity``: Parity (e.g., ``serial.PARITY_NONE``)

Only docstrings were added; functional behavior is unchanged.
"""

import logging

import serial_asyncio_fast
from serial import SerialException

from custom_components.elero.connection.config import SerialConfig
from custom_components.elero.connection.connection import Connection

_LOGGER = logging.getLogger(__name__)


class SerialConnection(Connection):
    """Connection class for Elero devices over direct serial (USB/COM port)."""

    # Class managing an asynchronous serial connection.

    def __init__(self, serial_config: SerialConfig) -> None:
        """Create a serial connection with the provided configuration.

        Args:
            serial_config: Serial port parameters (device, baudrate, etc.) used
                to initialize the underlying transport.
        """
        super().__init__(serial_config.device)
        self._serial_config = serial_config
        self._writer = None
        self._reader = None

    async def open_connection(self) -> None:
        """Open the serial connection using ``serial_asyncio_fast``.

        On success, the internal reader/writer streams are populated. Errors
        from the OS or the serial layer are logged and re-raised.
        """
        if not self.is_open():
            _LOGGER.debug("Opening serial connection to %s", self._port_name)
            try:
                reader, writer = await serial_asyncio_fast.open_serial_connection(
                    url=self._serial_config.device,
                    baudrate=self._serial_config.baudrate,
                    bytesize=self._serial_config.bytesize,
                    stopbits=self._serial_config.stopbits,
                    parity=self._serial_config.parity,
                )
                self._writer = writer
                self._reader = reader
            except (OSError, SerialException) as ex:
                _LOGGER.error("Failed to open serial port %s: %s", self._port_name, ex)
                raise
