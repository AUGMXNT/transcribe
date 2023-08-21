#!/bin/bash

if [ "$#" -eq 0 ]; then
  echo "An hf_token and approval is required for gated access for diarization models - see https://github.com/m-bain/whisperX#speaker-diarization"
  echo "Usage: $0 <hf_token>"
  exit 1
fi
time whisperx --model large-v2 --language en --output_format all --task transcribe --diarize --min_speakers 3 --max_speakers 3 --hf_token $1 Prompt\ -\ DR\ -\ Fred\ Benenson\ -\ AI\ \[1595724171\].mp3
