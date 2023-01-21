void setup() {
  pinMode(3, 1);

}

void loop() {
  digitalWrite(3, 1);
  delay(3000);
  digitalWrite(3, 0);
  delay(3000);
}
