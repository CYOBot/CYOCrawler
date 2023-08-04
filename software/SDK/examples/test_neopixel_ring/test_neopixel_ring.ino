#include <Adafruit_NeoPixel.h>
#include <list>
using namespace std;

// #define LED_PIN 16 // 26
// crawler v2.0 LED_PIN 13
#define LED_PIN 13
#define LED_COUNT 12

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

struct Pixel {
  byte red;
  byte green;
  byte blue;
};

void reset_matrix(){
  for(int i = 0; i < LED_COUNT; i++){
    strip.setPixelColor(i, strip.Color(0, 0, 0));
  }
  strip.show();
}

void set_all(Pixel pixel){
  for(int i = 0; i < LED_COUNT; i++){
    strip.setPixelColor(i, strip.Color(pixel.red, pixel.green, pixel.blue));
  }
  strip.show();
}

void set_manual(byte index, Pixel pixel){
  strip.setPixelColor(index, strip.Color(pixel.red, pixel.green, pixel.blue));
  strip.show();
}

//void set_character(char c, int offset = 0, Pixel pixel = {5, 5, 5}, bool multiplex = false){
//   byte* test_nested_list[9] = {};
//   byte test[5] = {1, 2, 3, 4, 5};
//   test_nested_list[0] = &test;
//}

void setup() {
  Serial.begin(9600);
  strip.begin();
  strip.setBrightness(100);
  strip.show(); // Initialize all pixels to 'off'
}

void loop(){
  Pixel pixel = {100, 0, 20};
  set_all(pixel);
  delay(2000);
  reset_matrix();
  delay(2000);
}
