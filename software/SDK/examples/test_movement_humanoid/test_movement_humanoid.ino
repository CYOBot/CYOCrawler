#include <Adafruit_PWMServoDriver.h>
#include <math.h>
#include "BluetoothSerial.h"
using namespace std;

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x43);

#define SERVOMIN  100 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // this is the 'maximum' pulse length count (out of 4096)
#define FREQUENCY 60

#define DELAY_TIME 1

typedef struct leg{
  byte lower;
  byte upper;
  byte centerOffsetLower;
  byte centerOffsetUpper;
  byte currentAngleLower;
  byte currentAngleUpper;
};

//############### CHANNEL OF SERVO ON PCA9685 ###################
// legx = {lower, upper}
leg leg0 = {10, 9};
leg leg1 = {3, 4};
leg leg2 = {7, 6};
leg leg3 = {2, 1};
//###############################################################

int pulseWidth(byte angle);
void dynamicServoAssignment();
void updateServoState();

//############################# PRE-WRITTEN FUNCTIONS  #############################################

void updateServoState(){
  pwm.setPWM(leg0.upper, 0, pulseWidth(leg0.currentAngleUpper));
  pwm.setPWM(leg0.lower, 0, pulseWidth(leg0.currentAngleLower));
  pwm.setPWM(leg1.upper, 0, pulseWidth(leg1.currentAngleUpper));
  pwm.setPWM(leg1.lower, 0, pulseWidth(leg1.currentAngleLower));
  pwm.setPWM(leg2.upper, 0, pulseWidth(leg2.currentAngleUpper));
  pwm.setPWM(leg2.lower, 0, pulseWidth(leg2.currentAngleLower));
  pwm.setPWM(leg3.upper, 0, pulseWidth(leg3.currentAngleUpper));
  pwm.setPWM(leg3.lower, 0, pulseWidth(leg3.currentAngleLower));
}

void dynamicServoAssignment(float leg0NewUpper, float leg0NewLower, float leg1NewUpper, float leg1NewLower, float leg2NewUpper, float leg2NewLower, float leg3NewUpper, float leg3NewLower){
  float leg0UpperDiff = float(leg0.currentAngleUpper) - leg0NewUpper;
  float leg0LowerDiff = float(leg0.currentAngleLower) - leg0NewLower;
  
  float leg1UpperDiff = float(leg1.currentAngleUpper) - leg1NewUpper;
  float leg1LowerDiff = float(leg1.currentAngleLower) - leg1NewLower;
  
  float leg2UpperDiff = float(leg2.currentAngleUpper) - leg2NewUpper;
  float leg2LowerDiff = float(leg2.currentAngleLower) - leg2NewLower;
  
  float leg3UpperDiff = float(leg3.currentAngleUpper) - leg3NewUpper;
  float leg3LowerDiff = float(leg3.currentAngleLower) - leg3NewLower;

  byte leg0CurrentUpper = leg0.currentAngleUpper;
  byte leg0CurrentLower = leg0.currentAngleLower;
  
  byte leg1CurrentUpper = leg1.currentAngleUpper;
  byte leg1CurrentLower = leg1.currentAngleLower;
  
  byte leg2CurrentUpper = leg2.currentAngleUpper;
  byte leg2CurrentLower = leg2.currentAngleLower;
  
  byte leg3CurrentUpper = leg3.currentAngleUpper;
  byte leg3CurrentLower = leg3.currentAngleLower;

  for(int i = 0; i < 50; i++){
    leg0.currentAngleLower = byte(constrain(leg0CurrentLower - float(i*0.02)*leg0LowerDiff, 0, 180));
    leg0.currentAngleUpper = byte(constrain(leg0CurrentUpper - float(i*0.02)*leg0UpperDiff, 0, 180));
    leg1.currentAngleLower = byte(constrain(leg1CurrentLower - float(i*0.02)*leg1LowerDiff, 0, 180));
    leg1.currentAngleUpper = byte(constrain(leg1CurrentUpper - float(i*0.02)*leg1UpperDiff, 0, 180));
    leg2.currentAngleLower = byte(constrain(leg2CurrentLower - float(i*0.02)*leg2LowerDiff, 0, 180));
    leg2.currentAngleUpper = byte(constrain(leg2CurrentUpper - float(i*0.02)*leg2UpperDiff, 0, 180));
    leg3.currentAngleLower = byte(constrain(leg3CurrentLower - float(i*0.02)*leg3LowerDiff, 0, 180));
    leg3.currentAngleUpper = byte(constrain(leg3CurrentUpper - float(i*0.02)*leg3UpperDiff, 0, 180));
    updateServoState();
    delay(DELAY_TIME);
  }
}

int pulseWidth(byte angle){
  float unit_angle = float(int(SERVOMAX - SERVOMIN)*0.005555);
  return angle*unit_angle + SERVOMIN;
}

//###############################################################
//###############################################################
//##################         START HERE           ###############
//###############################################################
//###############################################################

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(FREQUENCY);  // Analog servos run at ~60 Hz updates
  delay(10);

  SerialBT.begin("CYOCrawler"); //Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");

  /*
   * Write your BOCA offset value for each motor here
   */
  //############### OFFSET VALUE FOR EACH MOTOR ##################
  leg0.centerOffsetLower = 96;
  leg0.centerOffsetUpper = 90;
  leg1.centerOffsetLower = 100;
  leg1.centerOffsetUpper = 94;
  leg2.centerOffsetLower = 99;
  leg2.centerOffsetUpper = 82;
  leg3.centerOffsetLower = 105;
  leg3.centerOffsetUpper = 84;
  //##############################################################
//
//  leg0.currentAngleLower = leg0.centerOffsetLower;
//  leg0.currentAngleUpper = leg0.centerOffsetUpper + 45;
//  leg1.currentAngleLower = leg1.centerOffsetLower;
//  leg1.currentAngleUpper = leg1.centerOffsetUpper - 45;
//  leg2.currentAngleLower = leg2.centerOffsetLower - 80;
//  leg2.currentAngleUpper = leg2.centerOffsetUpper - 80;
//  leg3.currentAngleLower = leg3.centerOffsetLower + 80;
//  leg3.currentAngleUpper = leg3.centerOffsetUpper + 80;

  leg0.currentAngleLower = leg0.centerOffsetLower;
  leg0.currentAngleUpper = leg0.centerOffsetUpper;
  leg1.currentAngleLower = leg1.centerOffsetLower;
  leg1.currentAngleUpper = leg1.centerOffsetUpper;
  leg2.currentAngleLower = leg2.centerOffsetLower;
  leg2.currentAngleUpper = leg2.centerOffsetUpper;
  leg3.currentAngleLower = leg3.centerOffsetLower;
  leg3.currentAngleUpper = leg3.centerOffsetUpper;

  delay(2000);
//  standUp();
  updateServoState();
}

void fourPhaseGaitPropagation(int gait[8]){
  for(int i = 0; i < 4; i++){
    dynamicServoAssignment(
      leg0.centerOffsetUpper + gait[i*2+0], leg0.centerOffsetLower + gait[i*2+1], 
      leg1.centerOffsetUpper + gait[((i+3)*2+0)%8], leg1.centerOffsetLower + gait[((i+3)*2+1)%8], 
      leg2.centerOffsetUpper + gait[((i+1)*2+0)%8], leg2.centerOffsetLower + gait[((i+1)*2+1)%8], 
      leg3.centerOffsetUpper + gait[((i+2)*2+0)%8], leg3.centerOffsetLower + gait[((i+2)*2+1)%8]
    );
  }
}

void fourPhaseGaitPropagation_onlyLeg(int gait[8]){
  /*
   * only control the "leg" of the humanoid form -> 0 and 1
   * Upper of leg0 will be offset +45 and upper of leg1 will be offset -45
   */
  for(int i = 0; i < 4; i++){
    dynamicServoAssignment(
      leg0.currentAngleUpper, leg0.centerOffsetLower + gait[i*2+1], 
      leg1.centerOffsetUpper + gait[((i+3)*2+0)%8] + 45, leg1.centerOffsetLower + gait[((i+3)*2+1)%8],
      leg2.centerOffsetUpper - gait[((i+1)*2+0)%8] - 45, leg2.centerOffsetLower + gait[((i+1)*2+1)%8], 
      leg3.currentAngleUpper, leg3.centerOffsetLower + gait[((i+2)*2+1)%8]
    );
  }
}

void twoPhaseGaitPropagation(int gait[8]){
  for(int i = 0; i < 4; i++){
    dynamicServoAssignment(
      leg0.centerOffsetUpper + gait[((i)*2+0)%8], leg0.centerOffsetLower + gait[((i)*2+1)%8], 
      leg1.centerOffsetUpper + gait[((i+2)*2+0)%8], leg1.centerOffsetLower + gait[((i+2)*2+1)%8], 
      leg2.centerOffsetUpper + gait[((i)*2+0)%8], leg2.centerOffsetLower + gait[((i)*2+1)%8], 
      leg3.centerOffsetUpper + gait[((i+2)*2+0)%8], leg3.centerOffsetLower + gait[((i+2)*2+1)%8]
    );
  } 
}

void twoPhaseRotate(int gait[8]){
  for(int i = 0; i < 4; i++){
    dynamicServoAssignment(
      leg0.centerOffsetUpper + gait[((i)*2+0)%8], leg0.centerOffsetLower + gait[((i)*2+1)%8], 
      leg1.centerOffsetUpper + gait[((i+2)*2+0)%8], leg1.centerOffsetLower + gait[((i+2)*2+1)%8], 
      leg2.centerOffsetUpper - gait[((i)*2+0)%8], leg2.centerOffsetLower + gait[((i)*2+1)%8], 
      leg3.centerOffsetUpper - gait[((i+2)*2+0)%8], leg3.centerOffsetLower + gait[((i+2)*2+1)%8]
    );
  }
}

void standUp(){
  dynamicServoAssignment(
    leg0.centerOffsetUpper + 50, leg0.centerOffsetLower - 50,
    leg1.centerOffsetUpper + 45, leg1.centerOffsetLower + 45,
    leg2.centerOffsetUpper - 45, leg2.centerOffsetLower + 45,
    leg3.centerOffsetUpper - 50, leg3.centerOffsetLower - 50
  );
}

void duck(){
  dynamicServoAssignment(
    leg0.centerOffsetUpper + 50, leg0.centerOffsetLower + 40,
    leg1.centerOffsetUpper + 45, leg1.centerOffsetLower + 45,
    leg2.centerOffsetUpper - 45, leg2.centerOffsetLower + 45,
    leg3.centerOffsetUpper - 50, leg3.centerOffsetLower + 40
  );
}

void waveLeft(){
  dynamicServoAssignment(
    leg0.centerOffsetUpper - 20, leg0.centerOffsetLower + 40,
    leg1.centerOffsetUpper + 45, leg1.centerOffsetLower + 45,
    leg2.centerOffsetUpper - 45, leg2.centerOffsetLower + 45,
    leg3.centerOffsetUpper - 70, leg3.centerOffsetLower + 40
  );
}

void waveRight(){
  dynamicServoAssignment(
    leg0.centerOffsetUpper + 70, leg0.centerOffsetLower + 40,
    leg1.centerOffsetUpper + 45, leg1.centerOffsetLower + 45,
    leg2.centerOffsetUpper - 45, leg2.centerOffsetLower + 45,
    leg3.centerOffsetUpper + 20, leg3.centerOffsetLower + 40
  );
}

void testWorkout(){
  duck();
  delay(1000);
  standUp();
  delay(1000);
  duck();
  delay(1000);
  standUp();
  delay(1000);
  duck();
  delay(1000);
  standUp();
  delay(1000);
}

int forward_walk[] = {
  0, -20,
  -10, 0,
  +10, +20,
  0, -30
};

int backward_walk[] = {
  0, +20,
  -10, 0,
  +10, -20,
  0, +30
};

int mode = -1;

void dance() {
  fourPhaseGaitPropagation_onlyLeg(forward_walk);
  fourPhaseGaitPropagation_onlyLeg(backward_walk);
  fourPhaseGaitPropagation_onlyLeg(forward_walk);
  fourPhaseGaitPropagation_onlyLeg(backward_walk);
  standUp();
  duck();
  delay(200);

  fourPhaseGaitPropagation_onlyLeg(forward_walk);
  fourPhaseGaitPropagation_onlyLeg(backward_walk);
  fourPhaseGaitPropagation_onlyLeg(forward_walk);
  fourPhaseGaitPropagation_onlyLeg(backward_walk);
  standUp();
  duck();
  delay(200);

  fourPhaseGaitPropagation_onlyLeg(forward_walk);
  fourPhaseGaitPropagation_onlyLeg(backward_walk);
  fourPhaseGaitPropagation_onlyLeg(forward_walk);
  fourPhaseGaitPropagation_onlyLeg(backward_walk);
  standUp();
  duck();
  delay(200);
  
  waveLeft();
  waveRight();
  standUp();
  duck();
  delay(200);
  
  waveLeft();
  waveRight();
  standUp();
  duck();
  delay(200);
  
  waveLeft();
  waveRight();
  standUp();
  duck();
}

void loop() {
  if(SerialBT.available() > 0){
    byte data = SerialBT.read() - '0';
    if(data < 9 && data >= 0){
      mode = data; 
      SerialBT.println(mode);
      Serial.println(mode);
    }
  }

  switch(mode){
    case 0:{
      standUp();
      break;
    }
    case 1:{
      duck();
      break;
    }
    case 2:{
      fourPhaseGaitPropagation_onlyLeg(forward_walk);
      break;
    }
    case 3:{
      fourPhaseGaitPropagation_onlyLeg(backward_walk);
      break;
    }
    case 4:{
      dynamicServoAssignment(
        leg0.centerOffsetUpper, leg0.centerOffsetLower,
        leg1.centerOffsetUpper, leg1.centerOffsetLower,
        leg2.centerOffsetUpper, leg2.centerOffsetLower,
        leg3.centerOffsetUpper, leg3.centerOffsetLower
      );
      break;
    }
    case 5: {
      dance();
      mode = 1;
      break;
    }
    case 6: {
      testWorkout();
      mode = 1;
      break;
    }
    default:
      break;
  }
}
