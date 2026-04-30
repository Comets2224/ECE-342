#include <Arduino.h>
#include <ADC.h>
#include <ADC_util.h>
#include <USBHost_t36.h>
#include <stdio.h>
#include <inttypes.h>
#include <ctime>

#define PRId16 "hd"

u_int16_t command_code;

const int adc0ReadPin = A2;
const int adc1ReadPin = A0;

const size_t NUM_SAMPLES = 1250;

uint16_t samples_adc0[NUM_SAMPLES];
uint16_t samples_adc1[NUM_SAMPLES];

volatile uint32_t num_iter_adc0 = 0;
volatile uint32_t num_iter_adc1 = 0;

USBHost usb_host;

// Instances for one drive
USBDrive thumb(usb_host);

// Instances for accessing the files on the drive
USBFilesystem file_system(usb_host);

//char usb_buffer[2499];

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

void sample() {
  num_iter_adc0 = 0;
  num_iter_adc1 = 0;
  adc->startSynchronizedContinuous(adc0ReadPin, adc1ReadPin);

  while (num_iter_adc0 < NUM_SAMPLES || num_iter_adc1 < NUM_SAMPLES) {
    //Wait
  }

  adc->stopSynchronizedContinuous();
  
  uint16_t interleaved[NUM_SAMPLES * 2];
  for (size_t i = 0; i < NUM_SAMPLES; i++) {
    interleaved[i * 2] = samples_adc0[i];
    interleaved[i * 2 + 1] = samples_adc1[i];
  }

  Serial.write((uint8_t*)interleaved, NUM_SAMPLES * 4);
  Serial.flush();
}

void send_to_usb() {

  File output_file;

  usb_host.begin();
  usb_host.Task();
  delay(10000);

  while (!file_system) {
    usb_host.Task(); 
    delay(50);
  }

  digitalWrite(LED_BUILTIN, HIGH);
  
  //char file_name[25] = {'\0'};
  char output_buffer[7000] = {'\0'};

  char* end_of_buffer = output_buffer;
  for (size_t i = 0; i < NUM_SAMPLES; i++) {
    end_of_buffer += sprintf(end_of_buffer, "%hd,", samples_adc1[i]);
  }

  do {
    usb_host.Task();
    output_file = file_system.open("output.csv", FILE_WRITE_BEGIN);
    delay(50);
  }
  while (!output_file);

  output_file.write(output_buffer);
  output_file.close();
}

void setup() {

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

  // usb_host.begin();
  // delay(1000);

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(adc0ReadPin, INPUT_PULLUP);
  pinMode(adc1ReadPin, INPUT_PULLUP);

  Serial.begin(6000000);
}

void loop() {
  while (Serial.available() == 0) {
    //Wait
  }
  while (Serial.available()) {
    command_code = Serial.read();
    switch (command_code) {
      case 0x01:
        sample();
        break;
      case 0x02:
        break;
      case 0x03:
        send_to_usb();
        break;
    }
  }
  //usb_host.Task();
}
