import oscP5.*;
import netP5.*;

OscP5 oscP5;
/* a NetAddress contains the ip address and port number of a remote location in the network. */
NetAddress myBroadcastLocation; 


int numImages = 10;  //number of images
PImage[] sunImages = new PImage[numImages];
PImage[] ctrlImages = new PImage[numImages];

int imgDelay = 2000;
int sunImgNum = 0;
int ctrlImgNum = 0;

boolean isImg = false;

void setup() {
  background(100,100,100);
  //size(1920, 1080);
  fullScreen();
  
  frameRate(0.33);

  
  oscP5 = new OscP5(this,12000);  
  /* the address of the osc broadcast server */
  myBroadcastLocation = new NetAddress("127.0.0.1",5005);
  
  for (int i=0; i < sunImages.length; i++){
    String sunImg = String.format("sun/%d.jpg", i);
    String ctrlImg = String.format("ctrl/%d.jpg", i);    
    sunImages[i] = loadImage(sunImg);
    ctrlImages[i] = loadImage(ctrlImg);    
  } 
  
  println("Images Loaded!");
  delay(1000);
  
}

void draw() {
  
  if(!isImg){
    
    boolean r = randomBool();
    
    if(r && (sunImgNum < sunImages.length) ){
  
      println("Sun Image: " + sunImgNum);
  
      OscMessage myOscMessage = new OscMessage("/event");
      myOscMessage.add(1);
      oscP5.send(myOscMessage, myBroadcastLocation); 
      
      image(sunImages[sunImgNum], width/2 - 640, height/2-480, 1280, 960);     
      
      sunImgNum ++;

    
    }else if(ctrlImgNum < ctrlImages.length){
      
      println("Control Image: "  + ctrlImgNum);
  
      OscMessage myOscMessage = new OscMessage("/event");
      myOscMessage.add(0.5);
      oscP5.send(myOscMessage, myBroadcastLocation); 
      
      image(ctrlImages[ctrlImgNum], width/2 - 640, height/2-480, 1280, 960);   
      
      ctrlImgNum ++;
      
    }
    
    isImg=true;
    
  } else{
    background(100,100,100);
    isImg = false;
  }

}


boolean randomBool() {
  return random(1) > .5;
}
