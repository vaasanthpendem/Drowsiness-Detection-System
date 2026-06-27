#define GREEN_LED 2
#define RED_LED   4
#define BUZZER    15

void setup() {
  Serial.begin(115200);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED,   OUTPUT);
  pinMode(BUZZER,    OUTPUT);

  digitalWrite(GREEN_LED, HIGH); delay(300);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED,   HIGH); delay(300);
  digitalWrite(RED_LED,   LOW);
  digitalWrite(BUZZER,    HIGH); delay(100);
  digitalWrite(BUZZER,    LOW);

  digitalWrite(GREEN_LED, HIGH);
  Serial.println("ESP32 Drowsiness Alert Ready");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    if (cmd == 'D') {
      digitalWrite(GREEN_LED, LOW);
      digitalWrite(RED_LED,   HIGH);
      digitalWrite(BUZZER,    HIGH);
      Serial.println("STATUS:DROWSY");
    }
    else if (cmd == 'A') {
      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(RED_LED,   LOW);
      digitalWrite(BUZZER,    LOW);
      Serial.println("STATUS:ALERT");
    }
    else if (cmd == 'W') {
      digitalWrite(GREEN_LED, LOW);
      blinkRed(3);
      shortBeep(2);
      digitalWrite(GREEN_LED, HIGH);
      Serial.println("STATUS:WARNING");
    }
  }
}

void blinkRed(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(RED_LED, HIGH); delay(150);
    digitalWrite(RED_LED, LOW);  delay(150);
  }
}

void shortBeep(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER, HIGH); delay(100);
    digitalWrite(BUZZER, LOW);  delay(100);
  }
}