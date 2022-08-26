from controller import Controller
from modbus_client import ClientModbus
from time import sleep
from controller import Controller


def main():
    client = ClientModbus("localhost", 502)
    if not client.open_client():
        print("Nao encontrou o servidor")
        return

    print("Conectado ao servidor")
    dt = 0.2
    controller = Controller(
        lambda x: client.set_data("motor_state", x),
        lambda: client.get_data("motor_state"),
        lambda: client.get_data("level"),
        lambda x: client.set_data("desired_freq", x),
        lambda: client.get_data("temp_stator"),
        dt
    )

    controller.set_target(100)
    client.set_data("start_time", 2)
    client.set_data("valve_1", 1)
    # client.set_data("valve_2", 1)
    # client.set_data("valve_3", 1)

    print("start_time: ", client.get_data("start_time"))
    
    while True:
        sleep(dt/2)
        controller.control_step()
        sleep(dt/2)
        level = client.get_data("level")
        print(f"level: {level:2} -- "+\
            f"state: {client.get_data('motor_state'):1} -- "+\
            f"freq: {client.get_data('motor_freq'):.2f} / {controller._desired_freq:.2f} -- "+\
            f"temp: {client.get_data('temp_stator'):.2f} \r", end="")


if __name__ == "__main__":
    main()
