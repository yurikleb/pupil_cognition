import oscP5.*;
import netP5.*;

OscP5 oscP5;
/* a NetAddress contains the ip address and port number of a remote location in the network. */
NetAddress myBroadcastLocation; 


int numImages = 10;  //number of images

int sunImgNum = 0;
int ctrlImgNum = 0;

boolean isImg = false;
boolean r = true;

void setup() {
  background(100,100,100);
  //size(1920, 1080);
  fullScreen();
  
  frameRate(0.33);

  
  oscP5 = new OscP5(this,12000);  
  /* the address of the osc broadcast server */
  myBroadcastLocation = new NetAddress("127.0.0.1",5005);  
  delay(3000);
  
}

void draw() {
  
  if(!isImg){
    
    r = !r;
    
    if(r){
  
      println("Bright!");
  
      OscMessage myOscMessage = new OscMessage("/event");
      myOscMessage.add(1);
      oscP5.send(myOscMessage, myBroadcastLocation); 
      
      background(220,220,220);     
    
  }else{      
      
      println("Dark!");
  
      OscMessage myOscMessage = new OscMessage("/event");
      myOscMessage.add(0.5);
      oscP5.send(myOscMessage, myBroadcastLocation); 
      
      background(20,20,20); 
      
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
