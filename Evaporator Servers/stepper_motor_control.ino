String m = ""; String d = "";
int A[] = {3,5,7}; //Pin Order: {Step, Direction, Enable)}, A[] is Shutter Blade and B[] is Tip Rotator
int B[] = {31, 35, 39};
char rotstat;

void setup(){

  #define MS1 4
  #define MS2 5

int state=LOW;
  pinMode(A[0], OUTPUT);
  pinMode(A[1], OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(A[2], OUTPUT);
  pinMode(B[0], OUTPUT);
  pinMode(B[1], OUTPUT);
  pinMode(B[2], OUTPUT);
  digitalWrite(A[2], LOW);
  digitalWrite(B[2], LOW);
  Serial.begin(9600);
}

void loop(){
  if(Serial.available()){
    char rec;
    while (rec != 'r'){
      if(Serial.available()){
        rec = Serial.read();
        if(rec != 'r'){
          m += rec;
        }
        else if(rec == 'r'){
          if(m.endsWith("C") || m.endsWith("A")){ 
            Serial.print("turning\r\n");
            turn();
            m="";
          }
          else if(m == "i"){
            Serial.print("Stepper Motor Control\r\n");
            m="";
          }
          else if(m == "s"){
            Serial.print("stationary\r\n");
            m="";
          }
          else {
            Serial.print("Invalid entry.\r\n");
            m = "";
          }
        }
      }
    }
  }
}

void turn(){
  int stp; int dir; int x=0;
  String d = m.substring(1,m.length());
  String motor = ""; String direct = "";
  char stepper = m.charAt(0);
  if(stepper == 'A'){
    stp = (int)A[0]; dir = (int)A[1]; x = (d.toInt() * 8) / 1.8;
  }
  else if (stepper == 'B') {
    stp = (int)B[0]; dir = (int)B[1]; x = (d.toInt() * 8 * 60) / 1.8; 
  }
  int y=1;
  if(m.endsWith("C")){digitalWrite(dir, HIGH);}
  else if(m.endsWith("A")){digitalWrite(dir,LOW); }
  for(y= 1; y<x;y++) {
    digitalWrite(stp,HIGH); 
    delay(2);
    digitalWrite(stp,LOW); 
    delay(2);
    if(Serial.available()){
      rotstat = Serial.read();
      if(rotstat == 's'){
        Serial.print("turning\r\n");
      }
    }
  }
  while (Serial.available()){
    Serial.read();
  }
}

