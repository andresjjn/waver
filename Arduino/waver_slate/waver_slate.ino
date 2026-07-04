#include <Wire.h>
#include <stdint.h>

// I2C ///////////////////////

#define I2C_SDA 32
#define I2C_SCL 33
#define I2C_SLAVE_ADDRESS  0x11

struct {
  int16_t rightSpeed;
  int16_t leftSpeed;
} motorSpeed;

union {
  uint8_t raw[2];
  int16_t value;
} vel_l, vel_r;

////////////////////// End I2C

// Motors //////////////////////

const uint16_t PWMA = 25;
const uint16_t AIN2 = 17;
const uint16_t AIN1 = 21;
const uint16_t BIN1 = 22;
const uint16_t BIN2 = 23;
const uint16_t PWMB = 26;

const uint16_t ANALOG_WRITE_BITS = 8;

int freq = 100000;
int channel_A = 0;
int channel_B = 1;
int resolution = ANALOG_WRITE_BITS;

void initMotors(){
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  ledcSetup(channel_A, freq, resolution);
  ledcAttachPin(PWMA, channel_A);

  ledcSetup(channel_B, freq, resolution);
  ledcAttachPin(PWMB, channel_B);
}

void motorL(int16_t value){
  uint16_t pwm;
  if(value < 0){
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
    pwm = static_cast<uint16_t>(-value);
  } else {
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
    pwm = static_cast<uint16_t>(value);
  }
  // Serial.print("speedL: ");
  // Serial.println(value);
  ledcWrite(channel_A, pwm);
}

void motorR(int16_t value){
  uint16_t pwm;
  if(value < 0){
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
    pwm = static_cast<uint16_t>(-value);
  } else {
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
    pwm = static_cast<uint16_t>(value);
  }
  // Serial.print("speedR: ");
  // Serial.println(value);
  ledcWrite(channel_B, pwm);
}

////////////////////// End Motors

void moveF(int16_t vel_l, int16_t vel_r){
  // motors.setSpeeds(vel_l, vel_r);
  motorL(vel_l);
  motorR(vel_r);
}

// void receiveData(int byteCount);

void setup() {
  initMotors();
  Serial.begin(9600);

  Wire.begin(I2C_SLAVE_ADDRESS, I2C_SDA, I2C_SCL, 0);
  Wire.onReceive(receiveData);

  moveF(0, 0);

  // motorSpeed.rightSpeed = 0;
  // motorSpeed.leftSpeed  = 0;

//  motors.flipRightMotor(true);
}

void loop() {
  // moveF(100, -100);
  // delay(2000);
  // moveF(-100, 100);
  // delay(2000);
  // moveF(0, 0);
  // delay(2000);
  moveF(motorSpeed.leftSpeed, motorSpeed.rightSpeed);
}

// callback received data
void receiveData(int byteCount) {

  Serial.print("byteCount: ");
  Serial.println(byteCount);
    
  int8_t firstByte = Wire.read();

  vel_l.raw[1] = (int8_t) Wire.read();
  vel_l.raw[0] = (int8_t) Wire.read();

  vel_r.raw[1] = (int8_t) Wire.read();
  vel_r.raw[0] = (int8_t) Wire.read();

  motorSpeed.leftSpeed = vel_l.value;
  motorSpeed.rightSpeed = vel_r.value;

  Serial.print("firstByte: ");
  Serial.println(firstByte);

  Serial.print("leftSpeed: ");
  Serial.print(vel_l.value);
  Serial.print("\t rightSpeed: ");
  Serial.println(vel_r.value);
  
}