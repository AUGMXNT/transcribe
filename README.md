# transcribe

This is a simple transcription project done in 2023-08 intended to see what's possible with local AI tools.

# Setup

The assumption is that you are familiar w/ ML (UNIX/Python/Conda/Mamba), here are the required packages.

You will need CUDA.

```
# Basic environment
conda create -n transcribe
conda activate transcribe
# if you have multiple GPUs and just want to use one
conda env config vars set CUDA_VISIBLE_DEVICES=0
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

# OpenAI
pip install openai
```

# Transcription

[WhisperX](https://github.com/m-bain/whisperX) transcription of 33m file took 1m15s of wall time on a 3090 w/ large-v2 model.

WhisperX is great - super fast, and with the additional HF-gated models, you can do diarization effectively.

```
# get file
./01-get-mp3.sh

# run whisperx
./02-transcribe.sh

# assign speakers, etc - let's not stress the LLM too hard
./03-premunge.sh
```

I wrote a simple script [03-premunge.sh](03-premunge.sh) to assign the speaker names manually. I used the VTT (although the SRT would be almost the same) - the TXT output does not include the speakers.

# Additional Cleanup

## Initial Try

The end result is about 10K tokens. For cleanup, my original intention was to use on of the new "long" context (16K, 32K) windows a try. I started with the ([recently released](https://together.ai/blog/llama-2-7b-32k)) [togethercomputer/Llama-2-7B-32K-Instruct](https://huggingface.co/togethercomputer/Llama-2-7B-32K-Instruct) model.



The problems I ran into:

* libtiff.so.5 complaints
```
cd /usr/lib
ln -s libtiff.so.6 libtiff.so.5
```
* FlashAttention 2 having lib complaints - couldn't fix so just skipped it
* Could not run on 24GB GPU? (maybe if we had FlashAttention 2...)

I spent a fair amount of time already trying to get this to work already at this point so just moved on:
* https://huggingface.co/syzymon/long_llama_3b_instruct

It also was not happy. 0/2 for using `transformers`

Next I tried: [https://huggingface.co/TheBloke/LlongOrca-7B-16K-GGML](https://huggingface.co/TheBloke/LlongOrca-7B-16K-GGML)

So, it ran...:

```
❯ ~/llm/llama.cpp/main -ngl 99 --temp 0.1 --rope-freq-base 10000 --rope-freq-scale 0.25 -n 11000 -c 11000 -m /models/llm/llongorca/llongorca-7b-16k.ggmlv3.q8_0.bin -f prompt.txt > edit.txt
main: warning: scaling RoPE frequency by 0.25 (default 1.0)
main: warning: base model only supports context sizes no greater than 2048 tokens (11000 specified)
main: build = 1003 (097e121)
main: seed  = 1692631014
ggml_init_cublas: found 1 CUDA devices:
  Device 0: NVIDIA GeForce RTX 4090, compute capability 8.9
llama.cpp: loading model from /models/llm/llongorca/llongorca-7b-16k.ggmlv3.q8_0.bin
llama_model_load_internal: format     = ggjt v3 (latest)
llama_model_load_internal: n_vocab    = 32003
llama_model_load_internal: n_ctx      = 11000
llama_model_load_internal: n_embd     = 4096
llama_model_load_internal: n_mult     = 5504
llama_model_load_internal: n_head     = 32
llama_model_load_internal: n_head_kv  = 32
llama_model_load_internal: n_layer    = 32
llama_model_load_internal: n_rot      = 128
llama_model_load_internal: n_gqa      = 1
llama_model_load_internal: rnorm_eps  = 5.0e-06
llama_model_load_internal: n_ff       = 11008
llama_model_load_internal: freq_base  = 10000.0
llama_model_load_internal: freq_scale = 0.25
llama_model_load_internal: ftype      = 7 (mostly Q8_0)
llama_model_load_internal: model size = 7B
llama_model_load_internal: ggml ctx size =    0.08 MB
llama_model_load_internal: using CUDA for GPU acceleration
llama_model_load_internal: mem required  = 1089.91 MB (+ 5500.00 MB per state)
llama_model_load_internal: allocating batch_size x (512 kB + n_ctx x 128 B) = 944 MB VRAM for the scratch buffer
llama_model_load_internal: offloading 32 repeating layers to GPU
llama_model_load_internal: offloading non-repeating layers to GPU
llama_model_load_internal: offloading v cache to GPU
llama_model_load_internal: offloading k cache to GPU
llama_model_load_internal: offloaded 35/35 layers to GPU
llama_model_load_internal: total VRAM used: 13140 MB
llama_new_context_with_model: kv self size  = 5500.00 MB

system_info: n_threads = 16 / 32 | AVX = 1 | AVX2 = 1 | AVX512 = 0 | AVX512_VBMI = 0 | AVX512_VNNI = 0 | FMA = 1 | NEON = 0 | ARM_FMA = 0 | F16C = 1 | FP16_VA = 0 | WASM_SIMD = 0 | BLAS = 1 | SSE3 = 1 | VSX = 0 | 
sampling: repeat_last_n = 64, repeat_penalty = 1.100000, presence_penalty = 0.000000, frequency_penalty = 0.000000, top_k = 40, tfs_z = 1.000000, top_p = 0.950000, typical_p = 1.000000, temp = 0.100000, mirostat = 0, mirostat_lr = 0.100000, mirostat_ent = 5.000000
generate: n_ctx = 11000, n_batch = 512, n_predict = 11000, n_keep = 0


 [end of text]

llama_print_timings:        load time =  3120.85 ms
llama_print_timings:      sample time =    66.84 ms /   158 runs   (    0.42 ms per token,  2363.78 tokens per second)
llama_print_timings: prompt eval time =  6052.65 ms / 10134 tokens (    0.60 ms per token,  1674.31 tokens per second)
llama_print_timings:        eval time =  4101.42 ms /   157 runs   (   26.12 ms per token,    38.28 tokens per second)
llama_print_timings:       total time = 10251.37 ms
```

But gave frankly, terrible output. I didn't even bother saving it (bad! and this was w/ proper RoPE scaling)

## ChatGPT 4 Code Interpreter

It was getting late at the point so I decided to break out the big guns and see if ChatGPT-4 Code Interpreter could do better.

Here are the results:

* Transcript: [https://chat.openai.com/share/41f01738-637a-465c-a874-3c60e17fa2d1](https://chat.openai.com/share/41f01738-637a-465c-a874-3c60e17fa2d1)
* Output: [corrected_final_transcript.md](corrected_final_transcript.md)

The output it generated was not quite correct. It was trying very hard to use Python code to do all the fixups for some reason, and when I asked it to try to make more corrections, It went down the path of writing worse and worse regexes instead of being an LLM.

So, I started a new chat and I took that output and w/ a fresh context asked it to fix the transcript:

* Transcript: [https://chat.openai.com/share/d8306fbc-9034-4050-b028-e037e5f76b25](https://chat.openai.com/share/d8306fbc-9034-4050-b028-e037e5f76b25)
* Output: [secondtry-corrected_transcript.md](secondtry-corrected_transcript.md)

This output looks prety good, although I didn't validate it. I had to have it review piece by piece however, and it took quite a long time.

If we wanted to use a local model to do cleanup we would have to write our own code like w/ the CI to split lines, then pass into the local LLM to fix. If we used a llama2-70b it would be smart enough; we should try to figure out what's the smallest model that could help us...

## OpenAI Playground

Before the end of the night I did decide to see if just plain old `gpt-3.5-turbo-16k` could do the job, and while it ran out of tokens, it wasn't bad:

* [gpt-3.5-turbo-16k.md](https://github.com/AUGMXNT/transcribe/blob/main/gpt-3.5-turbo-16k.md)

## Properly Chunking w/ gpt-3.5-turbo-16k

The next day, I decided that the `gpt-3.5` results were good enough that I should try to do it properly. This resulted in the [05-gpt.py](05-gpt.py) script. It was relatively easy to chunk and submit and took about 5 minutes to run:
```
real    4m53.263s
user    0m0.481s
sys     0m2.186s
```

And the output [transcript-edited-by-gpt3.5.md](transcript-edited-by-gpt3.5.md) from a spot check looks like the best version so far.

## Can we do it locally?

Since I had the chunking code, I decided that I would try again with local models, especially with so many claiming to have reached parity with gpt-3.5...

If we do chunking, we don't need to futz w/ the long context models, so I tried some I had on hand (mostly Llama 2 models). Here are the results of some tests: 

* [local-output.md](local-output.md) - if you have a few min to give these a read, some of the output is hilarious, but most is just sad.

It looks like a 70B q4 model is maybe the smallest language mode that can actually instruction follow well enough to reformat text (This takes about 40GB of memory).

Here's the final results running [06-local-exllama.py](06-local-exllama.py) with the strongest model, a quant of [Orca Mini v3 70B](https://huggingface.co/psmathur/orca_mini_v3_70b)... it starts off OK, but sometimes goes terribly off the rails.

```
real    12m7.522s
user    12m23.434s
sys     0m16.600s
```

I gave a few other "strong" 70B models a try as well:

* [StableBeluga2 70B](https://stability.ai/blog/stable-beluga-large-instruction-fine-tuned-models) ([GPTQ](https://huggingface.co/TheBloke/StableBeluga2-70B-GPTQ)) - did not do **markdown** styling on speakers, added notes

* [Airoboros 2.0 70B](https://huggingface.co/jondurbin/airoboros-l2-70b-gpt4-2.0) - using the [context obedient question answering](https://huggingface.co/jondurbin/airoboros-l2-70b-gpt4-2.0) leads to some [*wild output*](output.airoboros-l2.txt)

While several open models have benchmarks approaching or even beating `gpt-3.5`, for instruction following it looks like there's a long ways to go to match OpenAI for a pretty "basic" task.

## Anthropic Claude

A friend tried Claude and it failed (potentially due to front-end safety filtering?). Still, now that I'm deep into it, why not write a script and see if the API will work or not? With 100K context, in theory, Claude should be able to give us a usable transcript without any chunking.

Hilariously, if you ask it for an sample script, Claude will hallucinate an API for you. Here's the [actual Python API]([GitHub - anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python)).

Our [first try](transcript-edited-by-claude2.md) dies at exactly 300s, so that's probably when the system kills a long-running call. Anthropics logs shows:

```json
{"client_error":true,"code":499,"detail":"Client disconnected"}
```

(*I didn't disconnect..*)

I adapted the gpt chunking code [07-claude.py](07-claude.py) and here's the [output from the second try](transcript-edited-by-claude2-try2.md).

* I didn't `time` it but from the logs it looks like took about 12 minutes, with most chunks (8) taking ~100s and a few a bit faster. (100 line chunks, 3000-4000 characters, unknown # of tokens, maybe 1000 tokens per chunk?)

* It looks like does a decent job, probably on par with gpt-3.5

* It manages to actually italicize all the Dutch, but also italicizes some non-Dutch as well.

* I noticed one or two line break errors.

* It does not remove "um"s (neither does gpt-3.5 though)
