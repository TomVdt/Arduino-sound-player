// Play a midi file (kinda) using only an arduino and some headphones!
// 2021-06
// By TomVdt


// These are the pins for my Arduino Nano clone, idk for the real one

// Pins for the left and right channels of the earphones
#define RIGHT 9
#define LEFT 11
// Activity indicator
#define LED_PIN 13


// Note structure containing the play duration, blank time and indices into 
// the frequency table (saves a LOT of space)
struct Note {
  const uint16_t note_duration;
  const uint16_t total_duration;
  const uint8_t index_left;
  const uint8_t index_right;
};
// File with all the data (easier to change music)
#include "audio_overworld.h"

// Code used to test things
//const int len_notes = 1;
//const int frequency_table[1] = {
//  30
//};
//const Note notes[1] = {
//  {5000,5000,0,0}
//};


void setup() {
  pinMode(RIGHT, OUTPUT);
  pinMode(LEFT, OUTPUT);

  digitalWrite(LED_PIN, HIGH);
}

// Initialise needed variables
unsigned long start_t = 0;
int current_note = 0;


void play_square(int pin, int frequency, float t) {
  // Simple square wave generator based on the sine function + a threshold (0 for perfect square)
  bool v = sin(2 * PI * frequency * t) > 0 ? HIGH : LOW;
  digitalWrite(pin, v);
}


void loop() {
  // Get the time (needed for the sine function)
  unsigned long current_t = micros();
  float t = current_t / 1e6;

  // Play a list of frequencies at a certain rate for a certain time (aka music)  
  // First we make sure that the time since the start of the note
  // does not exceed the note duration (allows for space between notes)
  
  if (current_t - start_t < notes[current_note].note_duration * 1e3) {
    play_square(LEFT, frequency_table[notes[current_note].index_left], t);
    play_square(RIGHT, frequency_table[notes[current_note].index_right], t);
  }

  // If the total duration of the note (playtime + silence),
  // prepare for the next note
  
  if (current_t - start_t > notes[current_note].total_duration * 1e3) {
    ++current_note;
    start_t = micros();

    // Do not exceed the length of the note array
    if (current_note > len_notes) {
      #ifdef DEBUG
      Serial.println("Done playing.");
      #endif

      // Clean up
      digitalWrite(LED_PIN, LOW);
      digitalWrite(LEFT, LOW);
      digitalWrite(RIGHT, LOW);
      // Give it time to finish
      delay(100);
      // Actually finish
      exit(0);
    }
  }
}
