import struct
import time
from typing import Any, List
from ..typings import EthOptions, UartOptions
from ..transfer.uart_transfer import UartTransfer
from ..transfer.eth_100base_t1_transfer import Eth100BaseT1Transfer
from ..devices.eth_device import (select_ethernet_interface, collect_devices)
from . import (create_transfer, create_eth_100base_t1_transfer)
from ..common import (message_helper, utils)


class TransferBase:
    def __init__(self) -> None:
        super().__init__()

    def on_initalize(self):
        pass

    def send(self, speed: int):
        pass


class LG69TUartTransfer(TransferBase):
    _transfer: UartTransfer

    def __init__(self, options: UartOptions) -> None:
        super().__init__()
        self._transfer = create_transfer(options)

        if not self._transfer:
            raise Exception('Cannot connect the LG69T Uart transfer, please check the configuration')

    def on_initalize(self):
        # set uart transfer mode
        message = message_helper.build_nmea_message(
            [
                'PQTMCFGDRMODE',
                '1',
                '2'
            ])
        self._transfer.send(message)
        time.sleep(0.1)
        # save configuration
        message = message_helper.build_nmea_message(
            [
                'PQTMSAVEPAR'
            ])
        self._transfer.send(message)

    def send_vehicle_speed(self, speed: int):
        # write uart message
        # build NMEA format message
        actual = speed*1000/3600
        message = message_helper.build_nmea_message(
            [
                'PQTMVEHMSG',
                '1',
                '0',
                str(actual)
            ])
        self._transfer.send(message)


class INS401EthernetTransfer(TransferBase):
    _transfer: Eth100BaseT1Transfer
    _src_mac: str
    _dst_mac_addresses: List[str]

    def __init__(self) -> None:
        super().__init__()

        iface = select_ethernet_interface()
        self._src_mac = iface.mac

        eth_devices = collect_devices(iface, self._src_mac)
        config = utils.get_config()

        if config["devices_mac"]:
            self._dst_mac_addresses = config["devices_mac"]
        else:
            self._dst_mac_addresses = [
                device.mac_address for device in eth_devices]

        self._transfer = create_eth_100base_t1_transfer(EthOptions(
            iface,
            self._src_mac,
            self._dst_mac_addresses))

        if not self._transfer:
            raise Exception('Cannot connect the INS401 100base-t1 transfer, please check the configuration')

    def on_initalize(self):
        print('[Info] Listen mac address list:')
        if len(self._dst_mac_addresses) == 0:
            print('[Info] No device detected')

        for address in self._dst_mac_addresses:
            print('MAC: {0}, SN: {1}'.format(
                address, utils.convert_mac_to_sn(address)))

    def send_vehicle_speed(self, speed: int):
        def build_eth_commands(devices_mac, local_mac, packet_type_bytes, message_bytes):
            commands = []
            for dest_mac in devices_mac:
                command = message_helper.build_eth_command(dest_mac, local_mac,
                                                           packet_type_bytes,
                                                           message_bytes)
                commands.append(command)

            return commands

        commands = build_eth_commands(self._dst_mac_addresses,
                                      self._src_mac,
                                      bytes([0x01, 0x0b]),
                                      list(struct.pack("<f", speed)))

        if self._transfer:
            self._transfer.send_batch(commands)


class TransferFactory:
    def create(config):
        protocol = config.get('protocol')
        provider = config.get('provider')
        if protocol == 'uart' and provider == 'lg69t':
            connection = config.get('connection')
            options = UartOptions(connection.get('path'), int(connection.get('baudrate')))
            transfer = LG69TUartTransfer(options)
            transfer.on_initalize()
            return transfer

        if protocol == '100base-t1' and provider == 'ins401':
            transfer = INS401EthernetTransfer()
            transfer.on_initalize()
            return transfer

        raise Exception('Unsupported can transfer configuration')


class TransferCenterError:
    _message: str
    _with_error: bool

    def __init__(self) -> None:
        self._message = ''
        self._with_error = False

    @property
    def message(self):
        return self._message

    @property
    def with_error(self):
        return self._with_error

    def set_error(self, value):
        self._message = value
        self._with_error = True

    def clear_error(self, value):
        self._with_error = False


class TransferCenter:
    _error: TransferCenterError
    _transfers: List[TransferBase]

    def __init__(self, config) -> None:
        self._error = TransferCenterError()
        self._transfers = []
        # build transfer from config
        if not isinstance(config, list):
            self._error.set_error('The configuration should be an array.')
            return

        for item in config:
            try:
                transfer = TransferFactory.create(item)
            except Exception as ex:
                self._error.set_error(ex)
                break

            self._transfers.append(transfer)

    def get_error(self):
        if self._error.with_error:
            return self._error
        return None

    def dispatch_vehicle_speed(self, speed):
        for transfer in self._transfers:
            transfer.send_vehicle_speed(speed)
