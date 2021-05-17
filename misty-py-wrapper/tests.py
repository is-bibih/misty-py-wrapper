from misty import Robot
from random import randrange
import numpy as np
import matplotlib.pyplot as plt
import time

alfredo = Robot('192.168.1.96')
debounce = 100 

# crear identificadores unicos
slam = 'slam' + str(randrange(0, 999))
imu = 'imu' + str(randrange(0, 999))

# enderezar la cabeza de misty
alfredo.head.move(0, 0, 0)

# comenzar a mapear
alfredo.stop_mapping()
print('stopping mapping...')
time.sleep(5)
alfredo.reset_slam()
print('resetting SLAM...')
time.sleep(10)
alfredo.start_mapping()
print('starting mapping...')

# suscribirse a slam 
alfredo.add_slam_status(slam, debounce=debounce)
alfredo.websockets[slam].subscribe()

# suscribirse a imu 
alfredo.add_imu(imu, debounce=debounce)
alfredo.websockets[imu].subscribe()

# girar hasta obtener pose
wait_time = 30 # segundos
alfredo.drive_time(0, 20, wait_time * 1000) # vel angular de 5%
has_pose = False
start_time = time.time()
while not has_pose and (time.time() - start_time < wait_time):
    print('in')
    slamMes = alfredo.websockets[slam].get_message()
    print(slamMes)
    if 'HasPose' in slamMes['slamStatus']['statusList']:
        has_pose = True
print(has_pose)
alfredo.stop()

# trazar cruz
for i in range(4):
    print(i)
    # 1) avanzar en linea recta (vel linear 10%, 3 s)
    alfredo.drive_time(10, 0, 3000)
    print('forward')
    # 2) dar una vuelta completa
    # posicion angular inicial
    heading = alfredo.websockets[imu].get_message()['yaw']
    print(heading)
    # empezar a dar vuelta
    alfredo.drive(0, 20)
    print('turn')
    finished_turn = False
    while not finished_turn:
        new_heading = alfredo.websockets[imu].get_message()['yaw']
        if (heading - 5) < new_heading < (heading + 5):
            finished_turn = True
    alfredo.stop()
    print('stop')
    # 3) regresar a posicion inicial (en reversa)
    alfredo.drive_time(-10, 0, 3000)
    print('backward')
    # 4) girar 90 grados
    heading = alfredo.websockets[imu].get_message()['yaw']
    goal = (heading + 90) % 360
    print(heading)
    print(goal)
    # emepezar a dar vuelta
    alfredo.drive(0, 20)
    print('next')
    finished_turn = False
    while not finished_turn:
        new_heading = alfredo.websockets[imu].get_message()['yaw']
        if (goal - 5) < new_heading < (goal + 5):
            finished_turn = True
    alfredo.stop()

input('continue?')

# obtener mapa
slam_map = alfredo.get_map()
print('map git')
grid = np.reshape(slam_map['grid'], (slam_map['height'], slam_map['width']))

# dejar de mapear
alfredo.stop_mapping()
print('stop map')
alfredo.websockets[slam].unsubscribe()
alfredo.websockets[imu].unsubscribe()
print('unsubscribe')

# mostrar mapa
plt.pcolormesh(grid)
plt.colorbar()
plt.savefig('map.png')

