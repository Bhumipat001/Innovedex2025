from pyfirmata2 import Arduino, util
import time

try:
    # Connect to the board
    board = Arduino('COM5')
    iterator = util.Iterator(board)
    iterator.start()
    
    print("Arduino connected successfully.")

    servo1 = board.get_pin('d:2:s')  # D2
    servo2 = board.get_pin('d:3:s')  # D3
    servo3 = board.get_pin('d:4:s')  # D4
    servo4 = board.get_pin('d:5:s')  # D5
    servo5 = board.get_pin('d:6:s')  # D6

    # Set servos to initial position

    offset1 = 4.5
    offset2 = 0
    servo1.write(90 + offset1)
    servo2.write(90 + offset2)
    servo3.write(90)
    servo4.write(120)
    servo5.write(60)

    # time.sleep(3)
    # servo4.write(170)
    # servo5.write(10)

    # time.sleep(3)
    # servo1.write(32 + offset1)
    # servo2.write(0  + offset2)
    # servo4.write(180)
    # servo5.write(20)
    

    def grip():
        servo4.write(178)
        servo5.write(2)
        time.sleep(1)

    def ungrip():
        servo4.write(140)
        servo5.write(60)
        time.sleep(1)

    # Normal movement height
    def defaultheight():
        servo3.write(175)

    # Height when storing donut
    def storeheight():
        #change 20 to desired height value, mm
        servo3.write(140) 

    # Height when pick up donut
    def pickheight():
        servo3.write(0) 

    def position1():
        servo1.write(146 + offset1)
        servo2.write(180 + offset2)
        # servo3.write(0)
        time.sleep(1)

    def position2():
        servo1.write(100 + offset1)
        servo2.write(180 + offset2)
        # servo3.write(0)
        time.sleep(1)

    def position3():
        servo1.write(84 + offset1)
        servo2.write(0  + offset2)
        # servo3.write(180)
        time.sleep(1)

    def position4():
        servo1.write(35 + offset1)
        servo2.write(3  + offset2)
        servo4.write(175)
        servo5.write(15)
        # servo3.write(90)
        time.sleep(1)

    def position5():
        servo1.write(120 + offset1)
        servo2.write(30 + offset2)
        # servo3.write(90)
        time.sleep(1)

    def pick1():
        # defaultheight()
        # time.sleep(0.6)
        position1()
        time.sleep(1)
        pickheight()
        time.sleep(0.6)
        grip()
        time.sleep(0.3)
        defaultheight()
        time.sleep(0.6)
        position4()
        time.sleep(1)
        storeheight()
        time.sleep(0.6)
        ungrip()
        time.sleep(0.3)

    def pick2():
        defaultheight()
        time.sleep(0.6)
        position2()
        time.sleep(1)
        pickheight()
        time.sleep(0.6)
        grip()
        time.sleep(0.3)
        defaultheight()
        time.sleep(0.6)
        position4()
        time.sleep(1)
        storeheight()
        time.sleep(0.6)
        ungrip()
        time.sleep(0.3)

    def pick3():
        defaultheight()
        time.sleep(0.6)
        position3()
        time.sleep(1)
        pickheight()
        time.sleep(0.6)
        grip()
        time.sleep(0.3)
        defaultheight()
        time.sleep(0.6)
        position4()
        time.sleep(1)
        storeheight()
        time.sleep(0.6)
        ungrip()
        time.sleep(0.3)

    def pick4():
        pickheight()
        time.sleep(0.6)
        grip()
        time.sleep(0.3)
        storeheight()
        time.sleep(0.6)
        position5()
        pickheight()
        time.sleep(0.6)
        time.sleep(1)
        ungrip()
        time.sleep(0.3)
        defaultheight()
        time.sleep(0.6)


except Exception as e:
    print(f"Error during initialization: {e}")
    if 'board' in locals():
        board.exit()