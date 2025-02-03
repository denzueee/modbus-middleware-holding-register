# modbus/urls.py

from django.urls import path
from modbus.views import ReadBitAPIView, WriteBitAPIView

urlpatterns = [
    path('read_holding_register', ReadBitAPIView.as_view(), name='read_bit'),
    path('write_holding_register', WriteBitAPIView.as_view(), name='write_bit'),
]
