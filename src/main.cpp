/*
File:     main.cpp
Author:   Tauno Erik
Started:  18.12.2022
Edited:   30.12.2022

Raspberry Pi Pico RP2040 default i2c pins
  SDA GP4
  SCL GP5
*/
#include <Arduino.h>
#include <Wire.h>

#define DEBUG
#include "utils_debug.h"

#include "Seeed_Arduino_GroveAI.h"

GroveAI ai(Wire);
uint8_t state = 0;


void setup() {
  Serial.begin(115200);
  delay(2000);
  DEBUG_PRINT("Begin");

  delay(1000);
  Wire.begin();
  DEBUG_PRINT("Wire.begin()");


  // Object detection and pre-trained model 1
  
  //ALGO_OBJECT_DETECTION
  //ALGO_OBJECT_COUNT
  //ALGO_IMAGE_CLASSIFICATION. 

/*
  while (!ai.begin(ALGO_OBJECT_DETECTION, MODEL_EXT_INDEX_2)) {
    delay(100);
    Serial.print("state 0");
  }
 
  state = 1;

  if (state == 1) {
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
  } else {
    Serial.println("Algo begin failed.");
  }
*/
int imu = ai.imu_start();
DEBUG_PRINT(imu);

}

void loop() {
  delay(100);
  if (ai.acc_available()) {
    //Serial.println("acc_available");
    Serial.print("acc_x ");
    Serial.print(ai.get_acc_x());
    Serial.print("acc_y ");
    Serial.print(ai.get_acc_y());
    Serial.print("acc_z ");
    Serial.println(ai.get_acc_z());
    
  }
  
  if (ai.gyro_available()) {
    //Serial.println("gyro_available");
    Serial.print("gyro_x ");
    Serial.print(ai.get_gyro_x());
    Serial.print("gyro_y ");
    Serial.print(ai.get_gyro_y());
    Serial.print("gyro_z ");
    Serial.println(ai.get_gyro_z());
  }
  /*
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
    //Serial.println("state == 0");
  }
*/
}
