# modbus/models.py

from django.db import models

class ModbusDevice(models.Model):
    host = models.CharField(max_length=100)
    port = models.IntegerField(default=502)

    def __str__(self):
        return f"{self.host}:{self.port}"
