from misty import Robot
import numpy as np
import matplotlib.pyplot as plt

alfredo = Robot('192.168.1.81')
debounce = 250

# comenzar a mapear
alfredo.start_mapping()

# suscribirse a slam 
alfredo.add_slam_status('slam', debounce=debounce)
alfredo.websockets['slam'].subscribe()

# suscribirse a imu 
alfredo.add_imu('imu', debounce=debounce)
alfredo.websockets['imu'].subscribe()

# girar hasta obtener pose
alfredo.drive(0, 5) # vel angular de 5%
has_pose = False
while not has_pose:
    slam = alfredo.websockets['slam'].get_message()
    if 'hasPose' in slam['statusList']:
        has_pose = True
alfredo.stop()

# trazar cruz
for i in range(4):
    # 1) avanzar en linea recta (vel linear 10%, 3 s)
    alfredo.drive_time(10, 0, 3000)
    # 2) dar una vuelta completa
    # posicion angular inicial
    heading = alfredo.websockets['imu'].get_message()['yaw']
    # empezar a dar vuelta
    alfredo.drive(0, 15)
    finished_turn = False
    while not finished_turn:
        new_heading = alfredo.websockets['imu'].get_message()['yaw']
        if (heading - 5) < new_heading < (heading + 5):
            finished_turn = True
    alfredo.stop()
    # 3) regresar a posicion inicial (en reversa)
    alfredo.drive_time(-10, 0, 3000)
    # 4) girar 90 grados
    heading = alfredo.websockets['imu'].get_message()['yaw']
    goal = (heading + 90) % 360
    # emepezar a dar vuelta
    alfredo.drive(0, 15)
    finished_turn = False
    while not finished_turn:
        new_heading = alfredo.websockets['imu'].get_message()['yaw']
        if (goal - 5) < new_heading < (goal + 5):
            finished_turn = True
    alfredo.stop()

# obtener mapa
slam_map = alfredo.get_map()
grid = np.reshape(slam_map['grid'], (slam_map['height'], slam_map['width']))

# dejar de mapear
alfredo.stop_mapping()

# mostrar mapa
plt.pcolormesh(grid)

