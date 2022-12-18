/*
File:     main.cpp
Author:   Tauno Erik
Started:  18.12.2022
Edited:   18.12.2022
*/
#include <Arduino.h>
#include "Seeed_Arduino_GroveAI.h"
#include <Wire.h>

/*
Raspberry Pi Pico RP2040 default i2c pins
  SDA GP4
  SCL GP5
*/

GroveAI ai(Wire);
uint8_t state = 0;


void setup() {
  Wire.begin();
  Serial.begin(115200);
  Serial.println("begin");

  // Object detection and pre-trained model 1
  if (ai.begin(ALGO_OBJECT_DETECTION, MODEL_EXT_INDEX_1)) {
    Serial.print("Version: ");
    Serial.println(ai.version());
    Serial.print("ID: ");
    Serial.println( ai.id());
    Serial.print("Algo: ");
    Serial.println( ai.algo());
    Serial.print("Model: ");
    Serial.println(ai.model());
    Serial.print("Confidence: ");
    Serial.println(ai.confidence());
    state = 1;
  } else {
    Serial.println("Algo begin failed.");
  }
}

void loop() {
  if (state == 1) {
    uint32_t tick = millis();

    // begin invoke
    if (ai.invoke()) {
      // wait for invoking finished
      while (1) {
        CMD_STATE_T ret = ai.state(); 
        if (ret == CMD_STATE_IDLE) {
          break;
        }
        delay(20);
      }

      uint8_t len = ai.get_result_len(); // receive how many people detect

      if(len) {
        int time1 = millis() - tick; 
        Serial.print("Time consuming: ");
        Serial.println(time1);
        Serial.print("Number of people: ");
        Serial.println(len);
        object_detection_t data;       //get data

        for (int i = 0; i < len; i++) {
          Serial.println("result:detected");
          Serial.print("Detecting and calculating: ");
          Serial.println(i+1);
          ai.get_result(i, (uint8_t*)&data, sizeof(object_detection_t)); //get result
  
          Serial.print("confidence:");
          Serial.print(data.confidence);
          Serial.println();
        }
      } else {
        Serial.println("No identification");
      }
    } else {
      delay(1000);
      Serial.println("Invoke Failed.");
    }
  } else {
    //Serial.println("state 0");
  }
}
