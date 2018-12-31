/**********************************
 * Nixie.ino
 * Author: Aeonni
 * Version: 0.3.0
 * Last Modified: 2018.10.7 
 * Blog: https://www.aeonni.com
 **********************************/
#include <MsTimer2.h>  
#include <TimerOne.h>
#include <Wire.h>
#include <DHT.h>
#include <DHT_U.h>
#include "pins.h"

#define I2C_ADDR 0x08

#define W_DELAY 1

#define COMP_FOR_TEST


DHT dht(DHT_SENSOR, DHT11);
char t_data[7] = "T:    ";
char h_data[7] = "H:    ";
char th_data[20];
char s_data[20];
String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
static unsigned int tm1_cnt = 1;
static unsigned int tm1_NixiePower_cntdn = 1;
bool th_detect = false;
bool do_display = true;
int lbtn = 0;
int rbtn = 0;
static int do_display_cntdn = 0;

void setup() {
  // initialize digital pins as output.
  pinMode(SHCP1, OUTPUT);
  pinMode(STCP1, OUTPUT);
  pinMode(DS1, OUTPUT);
  pinMode(OE1, OUTPUT);
  
  pinMode(SHCP2, OUTPUT);
  pinMode(STCP2, OUTPUT);
  pinMode(DS2, OUTPUT);
  pinMode(OE2, OUTPUT);

  pinMode(FAN, OUTPUT);
  pinMode(BREATH_LED, OUTPUT);
  pinMode(NIXIE_P, OUTPUT);

  pinMode(L_BUTTON, INPUT);
  pinMode(R_BUTTON, INPUT);
  
  // initialize digital pins' state
  digitalWrite(DS2, LOW);
  digitalWrite(SHCP2, LOW);
  digitalWrite(STCP2, LOW);
  digitalWrite(OE2, LOW);

  digitalWrite(DS1, LOW);
  digitalWrite(SHCP1, LOW);
  digitalWrite(STCP1, LOW);
  digitalWrite(OE1, LOW);

  digitalWrite(FAN, LOW);
  digitalWrite(NIXIE_P, LOW);

  // initialize i2c
  Wire.begin(I2C_ADDR);
  Wire.onReceive(receiveData);//从机 接收 主机 发来的数据
  Wire.onRequest(sendData); //从机 请求 主机 发送数据

  //wait for pi start
  int cnt = 0;
  while(1) {
    if (stringComplete) {
      if(inputString[0] == 'F'){
        printRGBP("aaaaaaaa");
        printNixie("        ");
        inputString = "";
        stringComplete = false;
        break;
      }
      inputString = "";
      stringComplete = false;
    }else{
      String str = "        ";
      str[cnt] = 'y';
      printRGBP(str);
      str = "        ";
      str[7-cnt] = '0';
      printNixie(str);
      digitalWrite(BREATH_LED, cnt % 2);
      cnt++;
      if(cnt == 8){
        cnt = 0;
      }
    }
    delay(500);
  }
  
  
  #ifdef COMP_FOR_TEST
    Serial.begin(115200);
    inputString.reserve(200);
  #endif
  
  MsTimer2::set(10, BreathFlower);        // 中断设置函数，每 500ms 进入一次中断
  MsTimer2::start();                //开始计时

  Timer1.initialize( 100000 ); //1000 = 1ms
  Timer1.attachInterrupt( tm1Event );
  
  attachInterrupt(0, L_ONCHANGE, CHANGE);
  attachInterrupt(1, R_ONCHANGE, CHANGE);
}


void loop() {

  if (stringComplete && do_display) {

    if(inputString[0] == 'L'){
      #ifdef COMP_FOR_TEST
        Serial.print("To RGB LED: ");
        Serial.println(inputString);
      #endif
      printRGBP(&inputString[1]);
    }else if(inputString[0] == 'N'){
      #ifdef COMP_FOR_TEST
        Serial.print("To Nixie Tube: ");
        Serial.println(inputString);
      #endif
      printNixie(&inputString[1]);
    }else if(inputString[0] == 'O'){
      #ifdef COMP_FOR_TEST
        Serial.print("Open Device: ");
        Serial.println(inputString);
      #endif
      switch(inputString[1]){
        case 'F': digitalWrite(FAN, HIGH); break;
        case 'N': digitalWrite(OE1, LOW); break;
        case 'L': digitalWrite(OE2, LOW); break;
        case 'P': digitalWrite(NIXIE_P, LOW); break;
        case 'B': MsTimer2::start(); break;
        default: break;
      }
    }else if(inputString[0] == 'C'){
      #ifdef COMP_FOR_TEST
        Serial.print("Close Device: ");
        Serial.println(inputString);
      #endif
      switch(inputString[1]){
        case 'F': digitalWrite(FAN, LOW); break;
        case 'N': digitalWrite(OE1, HIGH); break;
        case 'L': digitalWrite(OE2, HIGH); break;
        case 'P': digitalWrite(NIXIE_P, HIGH); break;
        case 'B': MsTimer2::stop(); break;
        default: break;
      }
    }else{
      ;
    }
    
    #ifdef COMP_FOR_TEST
    Serial.println("Done!\n");
    #endif
    // clear the string:
    inputString = "";
    stringComplete = false;
  }else if(stringComplete){
    inputString = "";
    stringComplete = false;
  }
  
  if(th_detect) {
    dtostrf(dht.readTemperature(),2,1,&t_data[2]);
    dtostrf(dht.readHumidity(),2,1,&h_data[2]);
    (String("")+t_data+h_data).toCharArray(th_data, 14);
    th_detect = false;
  }

}

static long l_downtime;
void L_ONCHANGE()
{
   if ( digitalRead(L_BUTTON) == LOW ){
   #ifdef COMP_FOR_TEST
      Serial.println("L Key Down");
   #endif
   l_downtime = millis();
   }else{
   #ifdef COMP_FOR_TEST
      Serial.print("L Key UP: ");
      Serial.println(millis() - l_downtime);
   #endif
      digitalWrite(NIXIE_P, LOW);
      tm1_NixiePower_cntdn = 1;
   }
}

static long r_downtime;
void R_ONCHANGE()
{
   if ( digitalRead(R_BUTTON) == LOW ){
   #ifdef COMP_FOR_TEST
      Serial.println("R Key Down");
   #endif
   r_downtime = millis();
   }else{
   #ifdef COMP_FOR_TEST
      Serial.print("R Key UP: ");
      Serial.println(millis() - r_downtime);
   #endif
      if((millis() - r_downtime) > 500){
        char s[9] = "        ";
        s[6] = th_data[2];
        s[5] = th_data[3];
        s[4] = th_data[5];
        s[2] = th_data[8];
        s[1] = th_data[9];
        s[0] = th_data[11];
        do_display = false;
        do_display_cntdn = 30;
        printNixie(s);
        printRGBP("yyyYaaaA");
      }
      digitalWrite(NIXIE_P, LOW);
      tm1_NixiePower_cntdn = 1;
   }
}


void tm1Event() {
  ++tm1_cnt;
  ++tm1_NixiePower_cntdn;
  if( tm1_cnt % 50 == 0) {
    th_detect = true;
  }
  if( tm1_NixiePower_cntdn % 200 == 0) {
    digitalWrite(NIXIE_P, HIGH);
  }
  if(!do_display){
    --do_display_cntdn;
  }
  if(do_display_cntdn == 0){
    do_display = true;
  }
}

void BreathFlower() {                 //中断处理函数，改变灯的状态
  static unsigned char breath_out = 255;
  static char breath_i = -1;
  if(breath_out == 255){
    breath_i = -1;
  }

  if(breath_out == 0){
    breath_i = 1;
  }

  analogWrite(BREATH_LED, breath_out);
  breath_out += breath_i;
}


void receiveData(int byteCount){
  while(Wire.available()) {
    char inChar = (char)Wire.read();
    inputString += inChar;
    if (inChar == '\n' ) {
      stringComplete = true;
    }
  }
  #ifdef COMP_FOR_TEST
    Serial.println("Receive EVENT!\n");
  #endif
}

void sendData() {
  #ifdef COMP_FOR_TEST
    Serial.println("Request EVENT!\n");
  #endif
  if(inputString[0] == 'D'){
    Wire.write(th_data);
    inputString = "";
  }else if(inputString[0] == 'S'){
    char ls[10] = "L:";
    char rs[10] = "R:";
    itoa(lbtn, &ls[2], 10);
    itoa(rbtn, &rs[2], 10);
    (String("")+ls+rs).toCharArray(s_data, 20);
    Wire.write(s_data);
    inputString = "";
  }
}

void printRGBP(String s) {
  String t = "0000";
  for(int i = 0; i < 8; i++) {
    switch(s[i]) {
      case 'R': t = "0111"; break;
      case 'G': t = "1011"; break;
      case 'B': t = "1101"; break;
      case 'A': t = "1001"; break;
      case 'Y': t = "0011"; break;
      case 'P': t = "0101"; break;
      default: ;
      case 'd': t = "1110"; break;
      case 'D': t = "1111"; break;
      case 'W': t = "0001"; break;
      case 'r': t = "0110"; break;
      case 'g': t = "1010"; break;
      case 'b': t = "1100"; break;
      case 'a': t = "1000"; break;
      case 'y': t = "0010"; break;
      case 'p': t = "0100"; break;
      case 'w': t = "0000"; break;
    }

    for(int j = 0; j < 4; j++) {
      if(t[j] == '0') {
        digitalWrite(DS2, LOW);
      }else {
        digitalWrite(DS2, HIGH);
      }
      digitalWrite(SHCP2, HIGH);
      delay(W_DELAY);
      digitalWrite(SHCP2, LOW);
    }
  }

  digitalWrite(STCP2, HIGH);
  delay(W_DELAY);
  digitalWrite(STCP2, LOW);
  
}

void printNixie(String s) {
  String t = "0000";
  for(int i = 0; i < 8; i++) {
    switch(s[i]) {
      case '0': t = "0000"; break;
      case '1': t = "0001"; break;
      case '2': t = "0010"; break;
      case '3': t = "0011"; break;
      case '4': t = "0100"; break;
      case '5': t = "0101"; break;
      case '6': t = "0110"; break;
      case '7': t = "0111"; break;
      case '8': t = "1000"; break;
      case '9': t = "1001"; break;
      
      default:  t = "1111"; break;
    }

    for(int j = 0; j < 4; j++) {
      if(t[j] == '0') {
        digitalWrite(DS1, LOW);
      }else {
        digitalWrite(DS1, HIGH);
      }
      digitalWrite(SHCP1, HIGH);
      delay(W_DELAY);
      digitalWrite(SHCP1, LOW);
    }
  }

  digitalWrite(STCP1, HIGH);
  delay(W_DELAY);
  digitalWrite(STCP1, LOW);
  
}
