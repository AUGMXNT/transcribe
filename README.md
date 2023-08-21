# transcribe
Simple transcription and cleanup using local libraries

# Setup
```
conda create -n transcribe
conda activate transcribe
conda env config vars set CUDA_VISIBLE_DEVICES=1
conda activate transcribe
mamba install pip
pip install yt-dlp

# WhisperX
mamba install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch-nightly -c nvidia
pip install git+https://github.com/m-bain/whisperx.git

# LLaMA-2-7B-32K
pip install transformers==4.31.0
pip install sentencepiece
pip install ninja
pip install flash-attn --no-build-isolation
pip install git+https://github.com/HazyResearch/flash-attention.git#subdirectory=csrc/rotary

pip install accelerate
pip install bitsandbytes
```
# Transcribe
WhisperX transcription of 33m file took 1m15s of wall time on a 3090 w/ large-v2 model

```
# get file
./01-get-mp3.sh

# run whisperx
./02-transcribe.sh

# assign speakers, etc - let's not stress the LLM too hard
./03-premunge.sh
```

# Cleanup
Let's see if we can do any cleanup. Let's give a fancy new "big" context model a try:
* https://huggingface.co/togethercomputer/LLaMA-2-7B-32K

Issues:
```
# libtiff.so.5 complaints?
cd /usr/lib
ln -s libtiff.so.6 libtiff.so.5

# FlashAttention2 being a baby (dll-hell) so skipped it.
# Switched to accelerate and bitsandbytes for some quant action
```
