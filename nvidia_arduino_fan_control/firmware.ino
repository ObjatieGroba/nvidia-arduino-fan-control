#define ICR 320
#define MAX_FLOW 80
#define DELAY_MS 50

const char FLOW_CHAR_START = '*';
const char FLOW_CHAR_END = FLOW_CHAR_START + MAX_FLOW + 1;
const byte PWM_PIN = 10;
const uint8_t FLOW_STEP = ICR / MAX_FLOW;

const char CHAR_VERSION = '!';
const char VERSION[] = "0.1\n";


void setPWM(uint8_t flow) {
    OCR1B = (uint16_t)(flow) * FLOW_STEP;
}


void setup() {
    Serial.begin(9600);

    pinMode(PWM_PIN, OUTPUT);

    setupTimer1();

    setPWM(MAX_FLOW / 2);
}

void setupTimer1() {
    // Set PWM frequency to about 25khz on pins 9,10 (timer 1 mode 10, no prescale, count to 320)
    TCCR1A = (1 << COM1A1) | (1 << COM1B1) | (1 << WGM11);
    TCCR1B = (1 << CS10) | (1 << WGM13);
    ICR1 = ICR;
    OCR1A = 0;
    OCR1B = 0;
}

void loop() {
    if (Serial.available()) {
        // accept byte as flow from 0 to 80
        // 320 == 80 * 4
        char flow;
        while (Serial.available()) {
            flow = Serial.read();
        }
        if (flow == CHAR_VERSION) {
            Serial.println(VERSION);
            return;
        }
        if (flow < FLOW_CHAR_START or flow >= FLOW_CHAR_END) {
            Serial.write('1');
            Serial.write('\n');
            return;
        }
        flow -= FLOW_CHAR_START;
        setPWM((uint8_t)flow);
        Serial.write('0');
        Serial.write('\n');
    }
    delay(DELAY_MS);
}
