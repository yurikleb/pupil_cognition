import oscP5.*;
import netP5.*;
import processing.video.*;

Movie myMovie;

OscP5 oscP5;
/* a NetAddress contains the ip address and port number of a remote location in the network. */
NetAddress myBroadcastLocation; 

void setup() {
  background(100,100,100);
  //size(1920, 1080);
  fullScreen();yuri0
  
  frameRate(30);

  myMovie = new Movie(this, "gorilla.mp4");
  myMovie.loop();
  
  oscP5 = new OscP5(this,12000);  
  /* the address of the osc broadcast server */
  myBroadcastLocation = new NetAddress("127.0.0.1",5005);
  delay(100);
  
}

void draw() {
  
      image(myMovie, width/2-512, height/2-384,1024,768);
      
      //println(frameCount);
      
      // Send a "1" if the gorilla is in frame or "0" if no gorilla is in frame.
      //at 30fps 850-1130, 1920-2180
      if((frameCount> 250 && frameCount < 350) || (frameCount> 675 && frameCount < 765)){
        OscMessage myOscMessage = new OscMessage("/event");
        myOscMessage.add(1);
        oscP5.send(myOscMessage, myBroadcastLocation);
      }else {
        OscMessage myOscMessage = new OscMessage("/event");
        myOscMessage.add(0);
        oscP5.send(myOscMessage, myBroadcastLocation);      
      }
      

}

// Called every time a new frame is available to read
void movieEvent(Movie m) {
  m.read();
}
