import oscP5.*;
import netP5.*;

OscP5 oscP5;
/* a NetAddress contains the ip address and port number of a remote location in the network. */
NetAddress myBroadcastLocation; 


int numImages = 6;  //number of images
PImage[] contentImages = new PImage[numImages];
PImage[] instructionImages = new PImage[2];
PImage[] exampleImages = new PImage[6];

float framerate = 30.0;
int imgDelay = 3; //Seconds
int frameCounter = 0;
int instructionsImgNum = 0;
int exampleImgNum = 0;
int contentImgNum = 0;

boolean isImg = false;
//boolean isImgTriggerSent = false;

//stages of the presentation 1: instructions 2:examples 3:experiment etc...
int stage = 3; 
int contentStartTime = 0;

//boolean isInstructions = true;
//boolean isExamples = true;
//boolean isContent = true;

void setup() {
  background(0,0,0);
  size(1920, 1080);
  //fullScreen();
  
  frameRate(framerate);
  
  oscP5 = new OscP5(this,12000);  
  /* the address of the osc broadcast server */
  myBroadcastLocation = new NetAddress("127.0.0.1",5005);
  
  for (int i=0; i < contentImages.length; i++){
    String img = String.format("%d.jpg", i);    
    contentImages[i] = loadImage(img);    
  } 
  
  for (int i=0; i < instructionImages.length; i++){
    String img = String.format("instructions/%d.jpg", i);    
    instructionImages[i] = loadImage(img);
  } 
  
  for (int i=0; i < exampleImages.length; i++){
    String img = String.format("examples/%d.jpg", i);    
    exampleImages[i] = loadImage(img);
  } 
  
  println("Images Loaded!");
  delay(3000);
  background(100,100,100);
  noStroke();
  textAlign(CENTER);
  rectMode(CENTER);
  
}

void draw() {
  
  frameCounter ++;
  
  if (keyPressed) {
    
    //Show grey screen between images
    if((key == ' ' && isImg == true)){
      
      //Show Grey screen for a few seonds after user found waldo and send OSC event
      sendOSCMsg(0.5);      
      drawGreyScreen();
      
      frameCounter = 0;
      isImg = false;
    
  }
        
  }else if (frameCounter > imgDelay * framerate && !isImg){

    switch(stage){
      case 1:
        showInstructions();
        break;
      case 2:
        showExamples();
        break;
      case 3:
        showContent();
        break;
    }

  }
  
  //if(stage == 3 && frameCounter > imgDelay && isImg){
  //  fill(100,100,100);
  //  rect(width/2,30,500,50);
  //  fill(0,0,0);
  //  textSize(32);
  //  int milli = (millis() - contentStartTime) % 1000; 
  //  int seconds = (millis() - contentStartTime) / 1000;
  //  int minutes = seconds / 60;
  //  String c = minutes + ":" + seconds + ":" + milli;
  //  text(c, width/2, 40);
  //}
  

}


void showInstructions(){
  //Show Instructions images   
  if (instructionsImgNum < instructionImages.length && !isImg){
    
    println("instructions img: " + instructionsImgNum);
    sendOSCMsg(stage);
    image(instructionImages[instructionsImgNum], width/2 - 640, height/2-480, 1280, 960);
    instructionsImgNum ++;
    isImg = true;
  
  }else if(instructionsImgNum >= instructionImages.length){
    
    stage = 2; 
    println("instructions end");

  }
}


void showExamples(){
  //Show Example images   
  if (exampleImgNum < exampleImages.length && !isImg){
    
    println("example img: " + exampleImgNum);
    sendOSCMsg(stage);
    image(exampleImages[exampleImgNum], width/2 - 640, height/2-480, 1280, 960);
    exampleImgNum ++;
    isImg = true;
  
  }else if(exampleImgNum >= exampleImages.length){
    
    stage = 3; 
    println("examples end");
  
  }
}


void showContent(){

  //Show Content images   
  if (contentImgNum < contentImages.length && !isImg){
    if (contentImgNum == 0){
      //Seave the time when content was shown for the 1st time
      contentStartTime = millis();
    }
    
    println("content img: " + contentImgNum);
    sendOSCMsg(stage);
    image(contentImages[contentImgNum], width/2 - 640, height/2-480, 1280, 960);
    contentImgNum ++;
    isImg = true;
  
  }else if(contentImgNum >= exampleImages.length){
    
    stage = 4; 
    println("Content end");
  
  }  

}

void sendOSCMsg(float val){
      
      OscMessage myOscMessage = new OscMessage("/event");
      myOscMessage.add(val);
      oscP5.send(myOscMessage, myBroadcastLocation);
      println("Sent: " + val);

}

void drawGreyScreen(){

      background(100,100,100);    
      isImg = false;
      //isImgTriggerSent = false;
      frameCounter = 0;

}

boolean randomBool() {
  return random(1) > .5;
}
