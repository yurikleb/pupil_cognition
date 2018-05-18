import oscP5.*;
import netP5.*;
import processing.video.*;

Movie myMovie;

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
  size(1920, 1080);
  //fullScreen();
  
  frameRate(30);

  myMovie = new Movie(this, "/media/yurikleb/Stuff/Repos/pupil_cognition/processing/vidPlayer/data/g.mov");
  myMovie.loop();
  
  oscP5 = new OscP5(this,12000);  
  /* the address of the osc broadcast server */
  myBroadcastLocation = new NetAddress("127.0.0.1",5005);
  delay(100);
  
}


// Called every time a new frame is available to read
void movieEvent(Movie m) {
  m.read();
}


void draw() {
  
      image(myMovie, 640, 360);
      
      //OscMessage myOscMessage = new OscMessage("/event");
      //myOscMessage.add(1);
      //oscP5.send(myOscMessage, myBroadcastLocation); 
      

}


boolean randomBool() {
  return random(1) > .5;
}
