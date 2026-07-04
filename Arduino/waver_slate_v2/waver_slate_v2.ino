// waver_slate_v2 — I2C slave firmware para Wave Rover (General Driver for Robots)
//
// Compatible con waver_slate v1: el registro 0x00 recibe velocidades de motor
// como dos int16 big-endian. Novedades:
//   - Registro 0x01: PWM de focos IO4/IO5 (2 bytes, 0-255 cada uno).
//   - Failsafe: si no llega comando de motor en WATCHDOG_MS, los motores paran.
//     El host debe reenviar comandos periodicamente (waver_base lo hace a 20 Hz).
//
// Protocolo I2C (esclavo en 0x11, SDA=32, SCL=33 — bus compartido con
// IMU QMI8658 0x6B, AK09918 0x0C, INA219 0x42, OLED 0x3C; el host los lee
// directamente, este firmware no los toca):
//   write [0x00, L_hi, L_lo, R_hi, R_lo]  -> motores
//   write [0x01, io4, io5]                -> focos

#include <Wire.h>
#include <stdint.h>

#define I2C_SDA 32
#define I2C_SCL 33
#define I2C_SLAVE_ADDRESS 0x11

#define REG_MOTORS 0x00
#define REG_LIGHTS 0x01

#define WATCHDOG_MS 1000

// Motores (driver TB6612, mismos pines que v1)
const uint16_t PWMA = 25;
const uint16_t AIN2 = 17;
const uint16_t AIN1 = 21;
const uint16_t BIN1 = 22;
const uint16_t BIN2 = 23;
const uint16_t PWMB = 26;

const uint16_t ANALOG_WRITE_BITS = 8;
const int MOTOR_FREQ = 100000;
const int channel_A = 0;
const int channel_B = 1;

// Focos IO4/IO5 (mismos pines/canales que el firmware stock de Waveshare)
#define IO4_PIN 4
#define IO5_PIN 5
const int IO4_CH = 7;
const int IO5_CH = 8;
const uint16_t LED_FREQ = 200;

// Estado compartido ISR <-> loop (la ISR de I2C solo escribe estos volatiles;
// todo el trabajo con hardware se hace en loop())
volatile int16_t targetLeft = 0;
volatile int16_t targetRight = 0;
volatile uint8_t targetIO4 = 0;
volatile uint8_t targetIO5 = 0;
volatile uint32_t lastMotorCmdMs = 0;

union Int16Bytes {
  uint8_t raw[2];
  int16_t value;
};

// Compatibilidad: el core arduino-esp32 3.x elimino ledcSetup/ledcAttachPin
// (ahora ledcAttach/ledcWrite trabajan por PIN); el 2.x usa canales.
#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
  #define PWM_ATTACH(pin, ch, freq)  ledcAttach(pin, freq, ANALOG_WRITE_BITS)
  #define PWM_WRITE(pin, ch, duty)   ledcWrite(pin, duty)
#else
  #define PWM_ATTACH(pin, ch, freq)  do { ledcSetup(ch, freq, ANALOG_WRITE_BITS); ledcAttachPin(pin, ch); } while (0)
  #define PWM_WRITE(pin, ch, duty)   ledcWrite(ch, duty)
#endif

void initMotors() {
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  PWM_ATTACH(PWMA, channel_A, MOTOR_FREQ);
  PWM_ATTACH(PWMB, channel_B, MOTOR_FREQ);
}

void initLights() {
  pinMode(IO4_PIN, OUTPUT);
  pinMode(IO5_PIN, OUTPUT);
  PWM_ATTACH(IO4_PIN, IO4_CH, LED_FREQ);
  PWM_ATTACH(IO5_PIN, IO5_CH, LED_FREQ);
}

void motorL(int16_t value) {
  uint16_t pwm;
  if (value < 0) {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
    pwm = static_cast<uint16_t>(-value);
  } else {
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
    pwm = static_cast<uint16_t>(value);
  }
  PWM_WRITE(PWMA, channel_A, min(pwm, (uint16_t)255));
}

void motorR(int16_t value) {
  uint16_t pwm;
  if (value < 0) {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
    pwm = static_cast<uint16_t>(-value);
  } else {
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
    pwm = static_cast<uint16_t>(value);
  }
  PWM_WRITE(PWMB, channel_B, min(pwm, (uint16_t)255));
}

void receiveData(int byteCount) {
  if (byteCount < 1) return;
  uint8_t reg = Wire.read();

  if (reg == REG_MOTORS && byteCount >= 5) {
    Int16Bytes l, r;
    l.raw[1] = Wire.read();
    l.raw[0] = Wire.read();
    r.raw[1] = Wire.read();
    r.raw[0] = Wire.read();
    targetLeft = l.value;
    targetRight = r.value;
    lastMotorCmdMs = millis();
  } else if (reg == REG_LIGHTS && byteCount >= 3) {
    targetIO4 = Wire.read();
    targetIO5 = Wire.read();
  }

  // Drena bytes sobrantes para no desincronizar el buffer
  while (Wire.available()) Wire.read();
}

void setup() {
  initMotors();
  initLights();
  Serial.begin(115200);

  Wire.begin(I2C_SLAVE_ADDRESS, I2C_SDA, I2C_SCL, 0);
  Wire.onReceive(receiveData);

  motorL(0);
  motorR(0);
  Serial.println("waver_slate_v2 ready");
}

void loop() {
  // Failsafe: sin comando reciente -> parada (las luces se mantienen)
  if (millis() - lastMotorCmdMs > WATCHDOG_MS) {
    motorL(0);
    motorR(0);
  } else {
    motorL(targetLeft);
    motorR(targetRight);
  }

  PWM_WRITE(IO4_PIN, IO4_CH, targetIO4);
  PWM_WRITE(IO5_PIN, IO5_CH, targetIO5);

  delay(10);
}
