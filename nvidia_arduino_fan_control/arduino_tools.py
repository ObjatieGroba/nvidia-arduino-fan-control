import sys
import time
import serial
import subprocess
import glob
from pathlib import Path


MAX_FLOW = 80
FLOW_CHAR_START = '*'
CHAR_VERSION = '!'
MIN_REQ_FIRMWARE = [0, 1]
RESTART_TIME_SECONDS = 3

FIRMWARE_PATH = Path(__file__).absolute().parent / 'firmware.ino'


class Nano:
    def __init__(self, port: str | None = None, autoupdate: bool = False):
        if port is None:
            # Try to find it automatically
            possible = glob.glob('/dev/ttyUSB*')
            if not possible:
                raise ValueError('No serial port detected')
            if len(possible) > 1:
                raise ValueError(f'More than one serial port detected: {", ".join(possible)}')
            self.port = possible[0]
        else:
            self.port = port
        self.serial: serial.Serial | None = None
        self._init_serial()
        self._check_update_firmware_version(autoupdate)

    def _check_update_firmware_version(self, autoupdate: bool = True, req: int = 3):
        print('Checking firmware version...', file=sys.stderr)
        if req == 0:
            raise ValueError('No firmware version detected. Can not update firmware.')
        try:
            version = self.get_firmware_version()
            if version >= MIN_REQ_FIRMWARE:
                return
        except Exception as e:
            print(e, file=sys.stderr)
            pass
        if not autoupdate:
            raise RuntimeError('Can not check firmware version.')
        if self.serial is not None:
            self.serial.close()
            self.serial = None
        self.upload_firmware()
        self._init_serial()
        self._check_update_firmware_version(autoupdate, req - 1)

    def _init_serial(self, baudrate: int = 9600, timeout: int = 1) -> None:
        self.serial = serial.Serial(port=self.port, baudrate=baudrate, timeout=timeout)
        time.sleep(RESTART_TIME_SECONDS)

    def set_pwm(self, flow: int) -> bool:
        if flow < 0 or flow > MAX_FLOW:
            raise ValueError(f'Signal must be between 0 and {MAX_FLOW}')
        if self.serial is None:
            self._init_serial()
            assert self.serial is not None
        print(f'Setting PWM {flow}/{MAX_FLOW}...', file=sys.stderr)
        self.serial.write(chr(ord(FLOW_CHAR_START) + flow).encode())
        err = self.serial.readline().strip()
        return err == b'0'

    def get_firmware_version(self) -> list[int]:
        if self.serial is None:
            self._init_serial()
            assert self.serial is not None
        print('Getting firmware version...', file=sys.stderr)
        assert self.serial.write(CHAR_VERSION.encode()) == len(CHAR_VERSION.encode())
        version = self.serial.readline()
        print(f'Got version: {version!r}', file=sys.stderr)
        return [int(v) for v in version.decode().strip().split('.', maxsplit=1)]

    def upload_firmware(self, path: str | Path = FIRMWARE_PATH) -> None:
        r = subprocess.run(['arduino', '--upload', path, '--port', self.port], capture_output=True, encoding='utf-8')
        if r.returncode != 0:
            print(r.stdout, file=sys.stderr)
            print(r.stderr, file=sys.stderr)
            raise RuntimeError(f'Arduino failed to upload firmware:\n{r.stderr}')
        time.sleep(RESTART_TIME_SECONDS)
