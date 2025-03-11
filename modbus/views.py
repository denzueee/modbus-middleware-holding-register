from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from modbus.models import ModbusDevice
from modbus.utils import ModbusClientWrapper, read_bit, write_bit


class ModbusAPIView(APIView):
    """
    Base API View for Modbus interactions.
    
    This class retrieves the Modbus device configuration from the database
    and provides `host` and `port` properties for subclasses to use.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modbus_device = self.get_modbus_device()

    def get_modbus_device(self):
        """
        Fetches the first Modbus device configuration from the database.

        Returns:
            ModbusDevice: The first Modbus device instance.

        Raises:
            Exception: If no Modbus device configuration is found.
        """
        try:
            return ModbusDevice.objects.first()
        except ModbusDevice.DoesNotExist:
            raise Exception("Modbus device configuration not found")

    @property
    def host(self) -> str:
        """Returns the Modbus server IP address."""
        return self.modbus_device.host

    @property
    def port(self) -> int:
        """Returns the Modbus server port."""
        return self.modbus_device.port


class ReadBitAPIView(ModbusAPIView):
    """
    API View to read a specific bit from a Modbus holding register.

    Query Parameters:
        - `register_address` (int): The register address (40001-based).
        - `bit_address` (int): The bit position (0-indexed).

    Returns:
        - `bit_value` (int): 1 if the bit is set, 0 otherwise.
    """

    def get(self, request):
        # Extract query parameters
        ip_address = request.query_params.get("ip_address")
        m_address = request.query_params.get("register_address")
        b_address = request.query_params.get("bit_address")

        # Validate input parameters
        if not all([ip_address, self.port, m_address, b_address]):
            return Response(
                {"error": "Missing parameters (register_address, bit_address)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client = ModbusClientWrapper(host=ip_address, port=self.port)

        if client.open():
            try:
                # Read the register value
                register_value = client.read_register(int(m_address))
                if register_value is None:
                    return Response(
                        {"error": f"Failed to read register {m_address}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Read the specific bit from the register
                bit_value = read_bit(register_value, int(b_address))
                return Response({
                    "message": "Address value read successfully",
                    "address": int(m_address),
                    "address_value": int(register_value),
                    "address_value_bit": int(bit_value)
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            finally:
                client.close()
        else:
            return Response(
                {"error": "Failed to connect to Modbus server"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WriteBitAPIView(ModbusAPIView):
    """
    API View to set or clear a specific bit in a Modbus holding register.

    Request Body (JSON):
        - `register_address` (int): The register address (40001-based).
        - `bit_address` (int): The bit position (0-indexed).
        - `bit_value` (int, optional): 1 to set the bit, 0 to clear it (default: 1).

    Returns:
        - Success message if the bit is written successfully.
    """

    def post(self, request):
        # Extract data from request
        ip_address = request.data.get("ip_address")
        m_address = request.data.get("register_address")
        b_address = request.data.get("bit_address")
        bit_value = request.data.get("bit_value", 1)  # Default to setting the bit (1)

        # Validate input parameters
        if not all([ip_address, self.port, m_address, b_address]):
            return Response(
                {"error": "Missing parameters (register_address, bit_address)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client = ModbusClientWrapper(host=ip_address, port=self.port)

        if client.open():
            try:
                # Read the current register value
                register_value = client.read_register(int(m_address))
                if register_value is None:
                    return Response(
                        {"error": f"Failed to read register {m_address}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Modify the specific bit in the register
                new_value = write_bit(register_value, int(b_address), int(bit_value))

                # Write the modified register value
                success = client.write_register(int(m_address), new_value)
                if not success:
                    return Response(
                        {"error": "Failed to write register"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                return Response({
                    "message": "Address value written successfully", 
                    "address": int(m_address),
                    "address_value": int(new_value),
                    "address_value_bit": int(bit_value)
                }, status=status.HTTP_200_OK,
)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            finally:
                client.close()
        else:
            return Response(
                {"error": "Failed to connect to Modbus server"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
