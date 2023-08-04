#include <Adafruit_NeoPixel.h>
#include <list>
using namespace std;

#define LED_PIN 33
//#define LED_COUNT 23
// crawler v2.0 LED_COUNT 33
#define LED_COUNT 33

Adafruit_NeoPixel matrix(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

struct Pixel {
  byte red;
  byte green;
  byte blue;
};

void reset_matrix(){
  for(int i = 0; i < LED_COUNT; i++){
    matrix.setPixelColor(i, matrix.Color(0, 0, 0));
  }
  matrix.show();
}

void set_all(Pixel pixel){
  for(int i = 0; i < LED_COUNT; i++){
    matrix.setPixelColor(i, matrix.Color(pixel.red, pixel.green, pixel.blue));
  }
  matrix.show();
}

void set_manual(byte index, Pixel pixel){
  matrix.setPixelColor(index, matrix.Color(pixel.red, pixel.green, pixel.blue));
  matrix.show();
}

//void set_character(char c, int offset = 0, Pixel pixel = {5, 5, 5}, bool multiplex = false){
//   byte* test_nested_list[9] = {};
//   byte test[5] = {1, 2, 3, 4, 5};
//   test_nested_list[0] = &test;
//}

void setup() {
  Serial.begin(9600);
  matrix.begin();
  matrix.setBrightness(100);
  matrix.show(); // Initialize all pixels to 'off'
}

void loop(){
  Pixel pixel = {100, 0, 20};
//  Pixel pixel = {10, 20, 10};
  set_all(pixel);
  delay(5000);
  reset_matrix();
  delay(5000);
}
