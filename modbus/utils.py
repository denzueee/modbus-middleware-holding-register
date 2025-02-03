# modbus/utils.py

from pyModbusTCP.client import ModbusClient

class ModbusClientWrapper:
    """
    A wrapper class for Modbus TCP client to handle reading and writing registers.
    
    Attributes:
        host (str): The IP address of the Modbus server.
        port (int): The port number for the Modbus connection.
        client (ModbusClient): An instance of the ModbusClient.
    """

    def __init__(self, host: str, port: int):
        """
        Initializes the Modbus client with the specified host and port.

        Args:
            host (str): The IP address of the Modbus server.
            port (int): The port number for the Modbus server.
        """
        self.host = host
        self.port = port
        self.client = ModbusClient(host=self.host, port=self.port)

    def open(self) -> bool:
        """
        Opens a connection to the Modbus server.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        return self.client.open()

    def close(self):
        """
        Closes the connection to the Modbus server.
        """
        self.client.close()

    def read_register(self, register: int) -> int:
        """
        Reads the value of a holding register.

        Args:
            register (int): The address of the register to read (zero-based).

        Returns:
            int: The value of the register if successful, None if an error occurs.
        """
        values = self.client.read_holding_registers(register, 1)
        return values[0] if values else None  # Handle None response safely

    def write_register(self, register: int, value: int) -> bool:
        """
        Writes a value to a single holding register.

        Args:
            register (int): The address of the register to write to (zero-based).
            value (int): The value to write to the register.

        Returns:
            bool: True if the write operation is successful, False otherwise.
        """
        return self.client.write_single_register(register, value)


def read_bit(register_value: int, bit_position: int) -> int:
    """
    Reads the bit_value of a specific bit within a register value.

    Args:
        register_value (int): The value of the register.
        bit_position (int): The bit position to read (0-based).

    Returns:
        int: 1 if the bit is set, 0 if the bit is clear.
    """
    return (register_value >> bit_position) & 0b00000001


def write_bit(register_value: int, bit_position: int, bit_value: int) -> int:
    """
    Modifies a specific bit in the register value.

    Args:
        register_value (int): The current value of the register.
        bit_position (int): The bit position to modify (0-based).
        bit_value (int): 1 to set the bit, 0 to clear the bit.

    Returns:
        int: The new register value with the modified bit.
    """
    if bit_value:
        return register_value | (1 << bit_position)  # Set bit
    else:
        return register_value & ~(1 << bit_position)  # Clear bit
