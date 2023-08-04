/*
 * Use this firmware and Serial input to find which servo goes to which channel of PCA
 * Use 0 and 1 to change the offset value of the chosen channel/motor
 * Use 2 and 3 to change between the channels
 * 
 * Write everything down so that you will implement this for further firmware
 */

#include <Adafruit_PWMServoDriver.h>
#include <math.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x43);

// Depending on your servo make, the pulse width min and max may vary, you 
// want these to be as small/large as possible without hitting the hard stop
// for max range. You'll have to tweak them as necessary to match the servos you
// have!
#define SERVOMIN  100 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // this is the 'maximum' pulse length count (out of 4096)
#define FREQUENCY 60

int pulseWidth(byte angle);
void wiggle();

int chosenChannel;
int centerOffsetAngleTest;

byte mode;

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);  // Analog servos run at ~60 Hz updates
  delay(10);
  
  for(int i = 0; i < 12; i++){
    pwm.setPWM(i, 0, pulseWidth(90));
  }
  
  delay(2000);

  chosenChannel = 0;
  centerOffsetAngleTest = 90;
}

int pulseWidth(byte angle){
  float unit_angle = float(int(SERVOMAX - SERVOMIN)*0.005555);
  return angle*unit_angle + SERVOMIN;
}

void wiggle(){
  for(int i = 90; i > 80; i--){
    pwm.setPWM(chosenChannel, 0, pulseWidth(i));
    delay(10);
  }
  for(int i = 80; i < 100; i++){
    pwm.setPWM(chosenChannel, 0, pulseWidth(i));
    delay(10);
  }
  for(int i = 100; i > 90; i--){
    pwm.setPWM(chosenChannel, 0, pulseWidth(i));
    delay(10);
  }
}

void loop() {
  int data = 4;
  if(Serial.available() > 0){
    data = Serial.read() - '0';
  }

  switch(data){
    case 0:
      centerOffsetAngleTest = constrain(centerOffsetAngleTest - 1, 0, 180);
      Serial.print("Current Channel: "); Serial.print(chosenChannel); Serial.print("       Current Offset: ");      
      Serial.println(centerOffsetAngleTest);
      break;
    case 1:
      centerOffsetAngleTest = constrain(centerOffsetAngleTest + 1, 0, 180);
      Serial.print("Current Channel: "); Serial.print(chosenChannel); Serial.print("       Current Offset: "); 
      Serial.println(centerOffsetAngleTest);
      break;
    case 2:
      chosenChannel = constrain(chosenChannel - 1, 0, 15);
      centerOffsetAngleTest = 90;
      wiggle();
      Serial.print("Current Channel: "); Serial.print(chosenChannel); Serial.print("       Current Offset: "); 
      Serial.println(centerOffsetAngleTest);
      break;
    case 3:
      chosenChannel = constrain(chosenChannel + 1, 0, 15);
      centerOffsetAngleTest = 90;
      wiggle();
      Serial.print("Current Channel: "); Serial.print(chosenChannel); Serial.print("       Current Offset: "); 
      Serial.println(centerOffsetAngleTest);
      break;
    default:
      break;
  }
  pwm.setPWM(chosenChannel, 0, pulseWidth(centerOffsetAngleTest));
}
