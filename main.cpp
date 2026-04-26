#include <Arduino.h>
#include <ADC.h>
#include <ADC_util.h>

const int adc0ReadPin = A2;
const int adc1ReadPin = A0;

const uint32_t NUM_SAMPLES = 1250;

uint16_t samples_adc0[NUM_SAMPLES];
uint16_t samples_adc1[NUM_SAMPLES];

volatile uint32_t num_iter_adc0 = 0;
volatile uint32_t num_iter_adc1 = 0;

ADC *adc = new ADC();

void adc0_isr(void) {
  uint16_t val = (uint16_t)adc->adc0->analogReadContinuous();
  if (num_iter_adc0 < NUM_SAMPLES) {
    samples_adc0[num_iter_adc0++] = val;
  }
}

void adc1_isr(void) {
  uint16_t val = (uint16_t)adc->adc1->analogReadContinuous();
  if (num_iter_adc1 < NUM_SAMPLES) {
    samples_adc1[num_iter_adc1++] = val;
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(adc0ReadPin, INPUT_PULLUP);
  pinMode(adc1ReadPin, INPUT_PULLUP);

  Serial.begin(6000000);
}

void loop() {
  while (Serial.available() == 0) {}
  while (Serial.available()) Serial.read();

  adc->adc0->setAveraging(1);
  adc->adc0->setResolution(10);
  adc->adc0->setConversionSpeed(ADC_settings::ADC_CONVERSION_SPEED::VERY_HIGH_SPEED);
  adc->adc0->setSamplingSpeed(ADC_settings::ADC_SAMPLING_SPEED::VERY_HIGH_SPEED);

  adc->adc1->setAveraging(1);
  adc->adc1->setResolution(10);
  adc->adc1->setConversionSpeed(ADC_settings::ADC_CONVERSION_SPEED::VERY_HIGH_SPEED);
  adc->adc1->setSamplingSpeed(ADC_settings::ADC_SAMPLING_SPEED::VERY_HIGH_SPEED);

  adc->adc0->enableInterrupts(adc0_isr);
  adc->adc1->enableInterrupts(adc1_isr);

  num_iter_adc0 = 0;
  num_iter_adc1 = 0;
  adc->startSynchronizedContinuous(adc0ReadPin, adc1ReadPin);

  while (num_iter_adc0 < NUM_SAMPLES || num_iter_adc1 < NUM_SAMPLES) {}

  adc->stopSynchronizedContinuous();

  uint16_t interleaved[NUM_SAMPLES * 2];
  for (uint32_t i = 0; i < NUM_SAMPLES; i++) {
    interleaved[i * 2]     = samples_adc0[i];
    interleaved[i * 2 + 1] = samples_adc1[i];
  }

  Serial.write((uint8_t*)interleaved, NUM_SAMPLES * 4);
  Serial.flush();
}
