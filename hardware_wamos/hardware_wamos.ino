
#include <SoftwareSerial.h>
// IMPORT ALL REQUIRED LIBRARIES
#include <NewPing.h>
#include <ArduinoJson.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <SPI.h>
#include <Wire.h>
   
//**********ENTER IP ADDRESS OF SERVER******************//

#define HOST_IP     "172.16.192.106"       // REPLACE WITH IP ADDRESS OF SERVER ( IP ADDRESS OF COMPUTER THE BACKEND IS RUNNING ON) 
#define HOST_PORT   "8080"            // REPLACE WITH SERVER PORT (BACKEND FLASK API PORT)
#define route       "api/update"      // LEAVE UNCHANGED 
#define idNumber    "620152511"       // REPLACE WITH YOUR ID NUMBER 

// WIFI CREDENTIALS
#define SSID        "MonaConnect"      // "REPLACE WITH YOUR WIFI's SSID"   
#define password    ""  // "REPLACE WITH YOUR WiFi's PASSWORD" 

#define stay        100
 
//**********PIN DEFINITIONS******************//

 
#define espRX         10
#define espTX         11
#define espTimeout_ms 300
 int trigPin=3;
 int echoPin=2;
 long duration;
 
 
/* Declare your functions below */
 

SoftwareSerial esp(espRX, espTX); 
 

void setup(){

  Serial.begin(115200); 
 
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

 

  espInit();  
 
}

void loop(){ 
   
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // read ultrasonic signals:
  pinMode(echoPin, INPUT);
  duration = pulseIn(echoPin, HIGH);

  // Convert the time into a distance
  double radar = (duration/2) / 74;

  double waterHeight = 77.763 - radar;

  double reserve = (3.1415 * pow(30.75,2)* waterHeight)/231.0;

  double percentage_left = (waterHeight / 77.763)*100;
   
  // send updates with schema ‘{"id": "student_id", "type": "ultrasonic", "radar": 0, "waterheight": 0, "reserve": 0, "percentage": 0}’

  StaticJsonDocument<1000>doc;
  char message[290]={0};

  doc["id"] = idNumber;
  doc["type"] = "ultrasonic";
  doc["radar"] = radar;
  doc["waterHeight"] = waterHeight;
  doc["reserve"] = reserve;
  doc["percentage"] = percentage_left;

  serializeJson(doc,message);
  espUpdate(message);



  delay(1000);  
}

 
void espSend(char command[] ){   
    esp.print(command); // send the read character to the esp    
    while(esp.available()){ Serial.println(esp.readString());}    
}


void espUpdate(char mssg[]){ 
    char espCommandString[50] = {0};
    char post[290]            = {0};

    snprintf(espCommandString, sizeof(espCommandString),"AT+CIPSTART=\"TCP\",\"%s\",%s\r\n",HOST_IP,HOST_PORT); 
    espSend(espCommandString);    //starts the connection to the server
    delay(stay);

    // GET REQUEST 
    // snprintf(post,sizeof(post),"GET /%s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n",route,HOST_IP,strlen(mssg),mssg);

    // POST REQUEST
    snprintf(post,sizeof(post),"POST /%s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s\r\n\r\n",route,HOST_IP,strlen(mssg),mssg);
  
    snprintf(espCommandString, sizeof(espCommandString),"AT+CIPSEND=%d\r\n", strlen(post));
    espSend(espCommandString);    //sends post length
    delay(stay);
    Serial.println(post);
    espSend(post);                //sends POST request with the parameters 
    delay(stay);
    espSend("AT+CIPCLOSE\r\n");   //closes server connection
   }

void espInit(){
    char connection[100] = {0};
    esp.begin(115200); 
    Serial.println("Initiallizing");
    esp.println("AT"); 
    delay(1000);
    esp.println("AT+CWMODE=1");
    delay(1000);
    while(esp.available()){ Serial.println(esp.readString());} 

    snprintf(connection, sizeof(connection),"AT+CWJAP=\"%s\",\"%s\"\r\n",SSID,password);
    esp.print(connection);

    delay(3000);  //gives ESP some time to get IP

    if(esp.available()){   Serial.print(esp.readString());}
    
    Serial.println("\nFinish Initializing");    
   
}

//***** Design and implement all util functions below ******
 

