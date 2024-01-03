from .pca9685 import PCA9685
import time
import json
import os

class Leg:
    def __init__(self, parent, upperServo, lowerServo, upperOrientationWRTHead = 1, lowerOrientationWRTHead = 1, centerOffsetUpper = 0, centerOffsetLower = 0):
        # the PCA
        if not isinstance(parent, PCA9685):
            raise TypeError("parent must be PCA9685 object")
        self.parent = parent
        self.upperServo = upperServo
        self.lowerServo = lowerServo
        self.centerOffsetUpper = centerOffsetUpper
        self.centerOffsetLower = centerOffsetLower
        self.currentAngleLower = 0
        self.currentAngleUpper = 0
        self.upperOrientationWRTHead = upperOrientationWRTHead
        self.lowerOrientationWRTHead = lowerOrientationWRTHead

    def setCurrentAngle(self, currentAngleLower, currentAngleUpper):
        self.currentAngleLower = currentAngleLower
        self.currentAngleUpper = currentAngleUpper

    def setOffset(self, centerOffsetUpper, centerOffsetLower):
        self.centerOffsetUpper = centerOffsetUpper
        self.centerOffsetLower = centerOffsetLower

    def updateServoState(self):
        self.parent.set_angle(self.upperServo, self.currentAngleUpper)
        self.parent.set_angle(self.lowerServo, self.currentAngleLower)

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

class Crawler:
    def __init__(self):
        self.pca = PCA9685()
        if "config.json" in os.listdir("/sd/lib/crawler"):
            print("config file found, loading...")
            with open("/sd/lib/crawler/config.json") as file:
                config = json.load(file)
            self.leg0 = Leg(self.pca, 
                config["leg0"]["upper"]["pin"], config["leg0"]["lower"]["pin"],
                config["leg0"]["upper"]["orientation"], config["leg0"]["lower"]["orientation"],
                config["leg0"]["upper"]["offset"], config["leg0"]["lower"]["offset"]
            )
            self.leg1 = Leg(self.pca, 
                config["leg1"]["upper"]["pin"], config["leg1"]["lower"]["pin"],
                config["leg1"]["upper"]["orientation"], config["leg1"]["lower"]["orientation"],
                config["leg1"]["upper"]["offset"], config["leg1"]["lower"]["offset"]
            )
            self.leg2 = Leg(self.pca, 
                config["leg2"]["upper"]["pin"], config["leg2"]["lower"]["pin"],
                config["leg2"]["upper"]["orientation"], config["leg2"]["lower"]["orientation"],
                config["leg2"]["upper"]["offset"], config["leg2"]["lower"]["offset"]
            )
            self.leg3 = Leg(self.pca, 
                config["leg3"]["upper"]["pin"], config["leg3"]["lower"]["pin"],
                config["leg3"]["upper"]["orientation"], config["leg3"]["lower"]["orientation"],
                config["leg3"]["upper"]["offset"], config["leg3"]["lower"]["offset"]
            )
            del config
        else:
            print("WARNING: no config file found for this CYOCrawler, use default setting. This can affect your CYOCrawler's performance. Please refer to the official tutorial to calibrate your CYOCrawler before using")
            self.leg0 = Leg(self.pca, 4, 5, -1, 1, 0, 0)
            self.leg1 = Leg(self.pca, 6, 7, -1, 1, 0, 0)
            self.leg2 = Leg(self.pca, 11, 10, 1, 1, 0, 0)
            self.leg3 = Leg(self.pca, 0, 1, 1, 1, 0, 0)
        self.DELAY_TIME = 0.002

    def updateServoState(self):
        self.leg0.updateServoState()
        self.leg1.updateServoState()
        self.leg2.updateServoState()
        self.leg3.updateServoState()

    def dynamicServoAssignment(self,
        leg0NewUpper, leg0NewLower,
        leg1NewUpper, leg1NewLower,
        leg2NewUpper, leg2NewLower,
        leg3NewUpper, leg3NewLower):
        leg0UpperDiff = self.leg0.currentAngleUpper - leg0NewUpper
        leg0LowerDiff = self.leg0.currentAngleLower - leg0NewLower
        leg1UpperDiff = self.leg1.currentAngleUpper - leg1NewUpper
        leg1LowerDiff = self.leg1.currentAngleLower - leg1NewLower
        leg2UpperDiff = self.leg2.currentAngleUpper - leg2NewUpper
        leg2LowerDiff = self.leg2.currentAngleLower - leg2NewLower
        leg3UpperDiff = self.leg3.currentAngleUpper - leg3NewUpper
        leg3LowerDiff = self.leg3.currentAngleLower - leg3NewLower

        leg0CurrentUpper = self.leg0.currentAngleUpper
        leg0CurrentLower = self.leg0.currentAngleLower
        leg1CurrentUpper = self.leg1.currentAngleUpper
        leg1CurrentLower = self.leg1.currentAngleLower
        leg2CurrentUpper = self.leg2.currentAngleUpper
        leg2CurrentLower = self.leg2.currentAngleLower
        leg3CurrentUpper = self.leg3.currentAngleUpper
        leg3CurrentLower = self.leg3.currentAngleLower

        for i in range(50):
            self.leg0.currentAngleLower = constrain(leg0CurrentLower - i*0.02*leg0LowerDiff, -90, 90)
            self.leg0.currentAngleUpper = constrain(leg0CurrentUpper - i*0.02*leg0UpperDiff, -90, 90)
            self.leg1.currentAngleLower = constrain(leg1CurrentLower - i*0.02*leg1LowerDiff, -90, 90)
            self.leg1.currentAngleUpper = constrain(leg1CurrentUpper - i*0.02*leg1UpperDiff, -90, 90)
            self.leg2.currentAngleLower = constrain(leg2CurrentLower - i*0.02*leg2LowerDiff, -90, 90)
            self.leg2.currentAngleUpper = constrain(leg2CurrentUpper - i*0.02*leg2UpperDiff, -90, 90)
            self.leg3.currentAngleLower = constrain(leg3CurrentLower - i*0.02*leg3LowerDiff, -90, 90)
            self.leg3.currentAngleUpper = constrain(leg3CurrentUpper - i*0.02*leg3UpperDiff, -90, 90)
            self.updateServoState()
            time.sleep(self.DELAY_TIME)
    
    def dynamicSingleServoAssignment(self, leg_index, new_upper, new_lower):
        legs = [self.leg0, self.leg1, self.leg2, self.leg3]

        legUpperDiff = legs[leg_index].currentAngleUpper - new_upper
        legLowerDiff = legs[leg_index].currentAngleLower - new_lower

        legCurrentUpper = legs[leg_index].currentAngleUpper
        legCurrentLower = legs[leg_index].currentAngleLower

        for i in range(50):
            legs[leg_index].currentAngleLower = constrain(legCurrentLower - i*0.02*legLowerDiff, -90, 90)
            legs[leg_index].currentAngleUpper = constrain(legCurrentUpper - i*0.02*legUpperDiff, -90, 90)
            self.updateServoState()
            time.sleep(self.DELAY_TIME)
    
    def readServoPosition(self, leg_index, joint_type):
        legs = [self.leg0, self.leg1, self.leg2, self.leg3]
        if joint_type == "upper":
            return legs[leg_index].currentAngleUpper
        elif joint_type == "lower":
            return legs[leg_index].currentAngleLower
    
    def centeredDynamicSingleServoAssignment(self, leg_index, new_upper, new_lower):
        legs = [self.leg0, self.leg1, self.leg2, self.leg3]
        self.dynamicSingleServoAssignment(
            leg_index,
            legs[leg_index].centerOffsetUpper + legs[leg_index].upperOrientationWRTHead * new_upper, 
            legs[leg_index].centerOffsetLower + legs[leg_index].lowerOrientationWRTHead * new_lower
        )
    
    def centeredDynamicServoAssignment(self, 
        leg0NewUpper, leg0NewLower,
        leg1NewUpper, leg1NewLower,
        leg2NewUpper, leg2NewLower,
        leg3NewUpper, leg3NewLower):
        self.dynamicServoAssignment(
            self.leg0.centerOffsetUpper + self.leg0.upperOrientationWRTHead * leg0NewUpper, self.leg0.centerOffsetLower + self.leg0.lowerOrientationWRTHead * leg0NewLower,
            self.leg1.centerOffsetUpper + self.leg1.upperOrientationWRTHead * leg1NewUpper, self.leg1.centerOffsetLower + self.leg1.lowerOrientationWRTHead * leg1NewLower,
            self.leg2.centerOffsetUpper + self.leg2.upperOrientationWRTHead * leg2NewUpper, self.leg2.centerOffsetLower + self.leg2.lowerOrientationWRTHead * leg2NewLower,
            self.leg3.centerOffsetUpper + self.leg3.upperOrientationWRTHead * leg3NewUpper, self.leg3.centerOffsetLower + self.leg3.lowerOrientationWRTHead * leg3NewLower
        )

    def twoPhaseGaitPropagation(self, gait, order=[1.0, 1.0, 1.0, 1.0]):
        for i in range(4):
            self.dynamicServoAssignment(
              self.leg0.centerOffsetUpper + order[0]*self.leg0.upperOrientationWRTHead * gait[((i)*2+0)%8], self.leg0.centerOffsetLower + self.leg0.lowerOrientationWRTHead * gait[((i)*2+1)%8],
              self.leg1.centerOffsetUpper + order[1]*self.leg1.upperOrientationWRTHead * gait[((i+2)*2+0)%8], self.leg1.centerOffsetLower + self.leg1.lowerOrientationWRTHead * gait[((i+2)*2+1)%8],
              self.leg2.centerOffsetUpper + order[2]*self.leg2.upperOrientationWRTHead * gait[((i)*2+0)%8], self.leg2.centerOffsetLower + self.leg2.lowerOrientationWRTHead * gait[((i)*2+1)%8],
              self.leg3.centerOffsetUpper + order[3]*self.leg3.upperOrientationWRTHead * gait[((i+2)*2+0)%8], self.leg3.centerOffsetLower + self.leg3.lowerOrientationWRTHead * gait[((i+2)*2+1)%8]
            )

    def stop(self):
        self.leg0.currentAngleUpper = self.leg0.centerOffsetUpper
        self.leg0.currentAngleLower = self.leg0.centerOffsetLower
        self.leg1.currentAngleUpper = self.leg1.centerOffsetUpper
        self.leg1.currentAngleLower = self.leg1.centerOffsetLower
        self.leg2.currentAngleLower = self.leg2.centerOffsetLower
        self.leg2.currentAngleUpper = self.leg2.centerOffsetUpper
        self.leg3.currentAngleLower = self.leg3.centerOffsetLower
        self.leg3.currentAngleUpper = self.leg3.centerOffsetUpper
        self.updateServoState()
        self.pca.all_off()
    
    def command(self, command):
        if command == "stop":
            self.stop()
        elif command == "forward":
            ## UP
            self.twoPhaseGaitPropagation([-20, -15, -20, +20, +30, +20, +30, -15])
        elif command == "backward":
            ## DOWN
            self.twoPhaseGaitPropagation([+20, -15, +20, +20, -30, +20, -30, -15])
        elif command == "rotate_left":
            ## TURN AROUND
            self.twoPhaseGaitPropagation([-30, -30, -30, 0, +30, +20, +30, 0], order=[-1.0, -1.0, 1.0, 1.0])
        elif command == "rotate_right":
            ## TURN AROUND
            self.twoPhaseGaitPropagation([-30, -30, -30, 0, +30, +20, +30, 0], order=[1.0, 1.0, -1.0, -1.0])
        elif command == "lateral_left":
            ## SIDE WALK LEFT
            self.twoPhaseGaitPropagation([-30, -30, -30, 0, +30, +20, +30, 0], order=[-1.0, 1.0, -1.0, 1.0])
        elif command == "lateral_right":
            ## SIDE WALK RIGHT
            self.twoPhaseGaitPropagation([-30, -30, -30, 0, +30, +20, +30, 0], order=[1.0, -1.0, 1.0, -1.0])