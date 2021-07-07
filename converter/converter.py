# MIDI to header file converter
# Works sometimes, use simple music for better results
# To use this, just change the "filename" with your file
# Make sure you are using the right track(s) (don't use to many)
#
# 2021-06
# By TomVdt


import mido


filename = "midi/marblemachine.mid"
tracks = [1]

filename_no_extension = filename.split(".")[0]
midi_file = mido.MidiFile(filename)


class Note:

	"""
		Note object representing frequencies to play on the left and right channel
		Attributes:
		 - self.note: MIDI note
		 - self.note_index: index of note in list of notes
		 - self.other_note: same as self.note, right channel
		 - self.other_note_index: same
		 - self.is_combined: flag to prevent note from being combined twice
		 - self.start: absolute start time of note (MIDI ticks)
		 - self.duration: note duration (MIDI ticks)
		 - self.end: relative ending time to next note (MIDI ticks)

		Methods:
		 - __init__: constructor, pretty dirty code
		 - add_note: add a note on the right channel (changes is_combined flag)
	"""

	def __init__(self, start, end, note):
		self.note = note
		self.note_index = 0
		self.other_note = note
		self.other_note_index = 0
		self.is_combined = False
		self.start = start
		self.end = end
		self.duration = end - start

	def add_note(self, note):
		self.other_note = note
		self.is_combined = True


def get_frequency(note):
	# https://en.wikipedia.org/wiki/MIDI_tuning_standard
	a = 440
	return int(2 ** ((note - 69) / 12) * a)


def get_tempo(mid):
	for track in mid.tracks:
		for msg in track:
			if msg.type == 'set_tempo':
				return msg.tempo
	else:
		# Default tempo.
		return 500000


def get_ms_per_tick(ticks_per_beat, tempo):
	# https://stackoverflow.com/questions/7063437/midi-timestamp-in-seconds
	return (tempo / ticks_per_beat) / 1000


def write_array(file, type, name, array, formating_rule):
	file.write(f"{type} {name}[{len(array)}] = {{\n")
	for i in range(len(array)):
		formated_string = formating_rule(array[i])
		file.write(formated_string)
		# Janky hack to avoid having to delete a character
		if i != len(array) - 1:
			file.write(",\n")
	file.write("\n};\n")


def write_output(file, notes, note_table):
	# Compute the max amount of notes for the available memory space
	# int is 2 bytes long, Note object is 2 + 2 + 1 + 1 = 6 bytes long
	note_size_limit = (2000 - 2 * len(note_table)) // 6

	# Write the length of the Notes array
	file.write(f"const int len_notes = {min(note_size_limit, len(notes)-1)};\n")

	# Array of frequencies
	write_array(file, "const uint16_t", "frequency_table", note_table, lambda x: f"\t{get_frequency(x)}")

	# Array of notes
	# Make sure notes does not exceed the arduino's capacity
	notes = notes[:min(note_size_limit, len(notes))]
	write_array(file, "Note", "notes", notes, lambda x: f"\t{{{int(x.duration)},{int(x.end)},{x.note_index},{x.other_note_index}}}")



def get_active(tick, events):
	active = []
	cummulated_time = 0
	for event in events:
		cummulated_time += event.time


def parse():
	# Get the ms per MIDI tick, useful for converting values later
	ms_per_tick = get_ms_per_tick(midi_file.ticks_per_beat, get_tempo(midi_file))

	# We only need note events
	# We also convert delta time to absolute time, makes calculation easier
	events = []
	for track in tracks:
		cummulated_time = 0
		for i in midi_file.tracks[track]:
			if not i.is_meta:
				if i.type == "note_on":
					cummulated_time += i.time
					i.time = cummulated_time
					events.append(i)
				if i.type == "note_off":
					cummulated_time += i.time
					i.time = cummulated_time
					events.append(i)

	# Associate every note_on event with its note_off event
	# Every note is then stored with start time, duration and MIDI note value
	notes = []
	midi_notes = []
	for i in range(len(events)):
		if events[i].type == "note_on":
			note = events[i].note
			time = events[i].time
			for j in range(i + 1, len(events)):
				if events[j].type == "note_off":
					if events[j].note == note:
						if not note in midi_notes:
							midi_notes.append(note)
						notes.append(Note(time, events[j].time, note))
						break

	# Group notes that start on the same time
	# Allows playing 2 frequencies at once
	combined_notes = []
	for i in range(len(notes)):
		if not notes[i].is_combined:
			start = notes[i].start
			for j in range(i + 1, len(notes)):
				if notes[j].start == start:
					notes[i].add_note(notes[j].note)
					notes[j].is_combined = True
			combined_notes.append(notes[i])
	
	# Complete note metadata, set the difference between current and next note start time
	# Allows for a more compact structure (16bit ints)
	notes = combined_notes
	# Make the array of frequencies pretty (purely cosmetic)
	midi_notes = sorted(midi_notes)
	for i in range(len(notes) - 1):
		notes[i].end = notes[i + 1].start - notes[i].start
		notes[i].start *= ms_per_tick
		notes[i].end *= ms_per_tick
		notes[i].duration *= ms_per_tick
		notes[i].note_index = midi_notes.index(notes[i].note)
		notes[i].other_note_index = midi_notes.index(notes[i].other_note)
	# Do not forget the last note !
	notes[-1].start *= ms_per_tick
	notes[-1].duration *= ms_per_tick
	notes[-1].end = notes[-1].duration
	notes[-1].note_index = midi_notes.index(notes[-1].note)
	notes[-1].other_note_index = midi_notes.index(notes[-1].other_note)

	write_output(open("../audio_" + filename_no_extension + ".h", "w+"), notes, midi_notes)

parse()



