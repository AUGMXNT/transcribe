# transcribe
Simple transcription and cleanup using local libraries

# Setup
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

# FlashAttention2 being a baby (dll-hell)
# UGH, if we skip it we run out of memory on a 24GB GPU. boourns
```

Let's not rathole...

Next: https://huggingface.co/syzymon/long_llama_3b_instruct
* Problems

Next: https://huggingface.co/TheBloke/LlongOrca-7B-16K-GGML

So, this ... runs:
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

But doesn't output correctly?