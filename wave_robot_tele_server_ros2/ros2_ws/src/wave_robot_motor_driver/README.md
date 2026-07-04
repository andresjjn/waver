# **Waver Motor Driver - ROS 2 Package**

This repository contains the **`waver_motor_driver`** package, a ROS 2 node designed to control the motors of the **Waver Rover** robot using a **Raspberry Pi 5** via the I2C protocol. This package allows sending commands to the rover's motor controllers through ROS 2 topics.

---

## **Features**
- Compatible with **Raspberry Pi 5** and the **Waver Rover** robot.
- Communicates with motor controllers using the I2C protocol.
- Receives speed and direction commands for the left and right motors.
- Easy integration into ROS 2-based robotic systems.

---

## **Requirements**
- **Raspberry Pi 5** with I2C enabled.
- **Waver Rover** robot with compatible motor controllers.
- ROS 2 (Humble, Foxy, or newer versions).
- Proper physical connection between the Raspberry Pi and the motor controller via I2C.

---

## **Usage**
1. Clone this repository into your ROS 2 workspace:
   ```bash
   git clone https://github.com/your-username/waver_motor_driver.git
   cd waver_motor_driver
   ```
2. Build the package:
   ```bash
   colcon build
   ```
3. Configure the I2C address and connect the Raspberry Pi to the motor controller.
4. Run the node:
   ```bash
   ros2 run waver_motor_driver motor_controller_node
   ```
5. Publish commands to the motor_commands topic to control the motors:
   ```bash
   ros2 topic pub /motor_commands std_msgs/msg/Int16MultiArray "{data: [100, -100]}"
   ```

## **Topics**
- /motor_commands (std_msgs/msg/Int16MultiArray): Array of two integers representing the speed and direction for the left and right motors of the Waver Rover.

## **Physical Connections**
- SDA (Data Line): GPIO 2 (Physical Pin 3).
- SCL (Clock Line): GPIO 3 (Physical Pin 5).
- GND (Ground): Any GND pin.
- VCC (Power): 3.3V or 5V pin (depending on the motor controller).

## **License**
This project is open-source and available under the MIT License.
