import oscP5.*;
import netP5.*;

OscP5 oscP5;
/* a NetAddress contains the ip address and port number of a remote location in the network. */
NetAddress myBroadcastLocation; 


int numImages = 5;  //number of images
PImage[] darkImages = new PImage[numImages];
PImage[] brightImages = new PImage[numImages];
PImage[] darkFlippedImages = new PImage[numImages];
PImage[] brightFlippedImages = new PImage[numImages];

int imgDelay = 2000;
int brightImgNum = 0;
int darkImgNum = 0;
int brightFlippedImgNum = 0;
int darkFlippedImgNum = 0;


boolean isImg = false;

void setup() {
  background(100,100,100);
  //size(1920, 1080);
  fullScreen();
  
  frameRate(0.33);

  
  oscP5 = new OscP5(this,12000);  
  /* the address of the osc broadcast server */
  myBroadcastLocation = new NetAddress("127.0.0.1",5005);
  
  for (int i=0; i < darkImages.length; i++){

    String brightImg = String.format("bright/%d.jpg", i);
    String darkImg = String.format("dark/%d.jpg", i);
    String brightFlippedImg = String.format("brightFlipped/%d.jpg", i);
    String darkFlippedImg = String.format("darkFlipped/%d.jpg", i);    
    
    brightImages[i] = loadImage(brightImg);    
    darkImages[i] = loadImage(darkImg);
    brightFlippedImages[i] = loadImage(brightFlippedImg);    
    darkFlippedImages[i] = loadImage(darkFlippedImg);
    
  } 
  
  println("Images Loaded!");
  delay(3000);
  
}

void draw() {
  
  if(!isImg){
    while(!isImg){
      
      int r = int(random(1,5)); //randomBool();
      println(r);
      
      if(r == 1 && (brightImgNum < brightImages.length) ){
    
        println("Bright Image: " + brightImgNum);
    
        OscMessage myOscMessage = new OscMessage("/event");
        myOscMessage.add(1);
        oscP5.send(myOscMessage, myBroadcastLocation); 
        
        image(brightImages[brightImgNum], width/2 - 640, height/2-480, 1280, 960);     
        
        brightImgNum ++;
        isImg=true;
      }
      
      if(r == 2 && (brightFlippedImgNum < brightFlippedImages.length) ){
    
        println("Bright Flipped Image: " + brightFlippedImgNum);
    
        OscMessage myOscMessage = new OscMessage("/event");
        myOscMessage.add(1.5);
        oscP5.send(myOscMessage, myBroadcastLocation); 
        
        image(brightFlippedImages[brightFlippedImgNum], width/2 - 640, height/2-480, 1280, 960);     
        
        brightFlippedImgNum ++;
        isImg=true;
      }    
      
      if(r == 3 && (darkImgNum < darkImages.length)){
        
        println("Dark Image: "  + darkImgNum);
    
        OscMessage myOscMessage = new OscMessage("/event");
        myOscMessage.add(0);
        oscP5.send(myOscMessage, myBroadcastLocation); 
        
        image(darkImages[darkImgNum], width/2 - 640, height/2-480, 1280, 960);   
        
        darkImgNum ++;
        isImg=true;      
      }
      
      if(r == 4 && (darkFlippedImgNum < darkFlippedImages.length)){
        
        println("Dark Flipped Image: "  + darkFlippedImgNum);
    
        OscMessage myOscMessage = new OscMessage("/event");
        myOscMessage.add(0.5);
        oscP5.send(myOscMessage, myBroadcastLocation); 
        
        image(darkFlippedImages[darkFlippedImgNum], width/2 - 640, height/2-480, 1280, 960);   
        
        darkFlippedImgNum ++;
        isImg=true;      
      }
    }   
  
  }else{
    background(100,100,100);
    isImg = false;
  }

}


boolean randomBool() {
  return random(1) > .5;
}
