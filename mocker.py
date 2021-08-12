import time
import threading
from packages.common.utils import print_message
from packages.typings import CanOptions
from packages.other.car_mocker import CARMocker


def car_message_gen_task():
    try:
        car_mocker = CARMocker(CanOptions('can0', 500000))
        while True:
            car_mocker.gen_random_speed()
            time.sleep(0.1)

    except Exception as ex:
        print_message('[Error] CAN log task has error')
        print_message('[Error] Reason:{0}'.format(ex))


if __name__ == '__main__':
    print_message('[Info] CAR mocker started.')

    threading.Thread(target=car_message_gen_task).start()

    while True:
        time.sleep(1)
