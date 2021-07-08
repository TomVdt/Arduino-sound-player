# Arduino simple frequency player

Play MIDI files (more like a sequence of frequencies) using only an Arduino and some headphones!

# Usage

If you for some reason want to try this, go ahead!

![Schematic](/img/schematic.png)

After having assembled the circuit above, you can begin the converting process
1. Use the (janky) converting script (requires mido)
1. Copy the outputed .h file to the "player" folder
1. Change the `#include "filename.h"` to your file
1. Verify that it compiles
1. Upload it to your arduino and pray

# About

This is the code I used for a school project. 
The original intent was simply to play a few frequencies with the arduino and headphones, but I was curious and wanted to see if I could make it play music!
A video of it in actions is not ready yet, I'll maybe update this repo... someday.