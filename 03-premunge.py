#!/usr/bin/env python

def replace_speakers_and_strip_timestamps(vtt_content, speakers_map):
    lines = vtt_content.split("\n")
    new_content = []
    for line in lines:
        # Skip lines with timestamps
        if '-->' in line:
            continue
        if 'WEBVTT' in line:
            continue

        # Replace speaker tags with names from the dictionary
        for speaker_tag, name in speakers_map.items():
            line = line.replace(speaker_tag, name)

        new_content.append(line)
    
    return "\n".join(new_content)

def process_vtt_file(filename, speakers_map):
    with open(filename, 'r') as file:
        vtt_content = file.read()

    new_content = replace_speakers_and_strip_timestamps(vtt_content, speakers_map)

    output_filename = 'transcript.txt'
    with open(output_filename, 'w') as file:
        file.write(new_content)

# Example usage
filename = 'Prompt - DR - Fred Benenson - AI [1595724171].vtt'
speakers_map = {
    '[SPEAKER_00]': 'Henrik',
    '[SPEAKER_01]': 'Marcel',
    '[SPEAKER_02]': 'Fred',
}

process_vtt_file(filename, speakers_map)

