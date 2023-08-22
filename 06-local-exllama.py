from model import ExLlama, ExLlamaCache, ExLlamaConfig
from tokenizer import ExLlamaTokenizer
from generator import ExLlamaGenerator
import os, glob
import sys
import torch

# https://huggingface.co/TheBloke/OpenAssistant-Llama2-13B-Orca-8K-3319-GPTQ
# model_directory =  "/models/llm/openassistant/TheBloke_OpenAssistant-Llama2-13B-Orca-8K-3319-GPTQ/"
model_directory =  "/models/llm/gptq/llama2/TheBloke_orca_mini_v3_70B-GPTQ/"
# model_directory =  "/models/llm/gptq/llama2/TheBloke_orca_mini_v3_13B-GPTQ/"
# model_directory =  "/models/llm/gptq/llama2/TheBloke_orca_mini_v3_7B-GPTQ/"

# Locate files we need within that directory
tokenizer_path = os.path.join(model_directory, "tokenizer.model")
model_config_path = os.path.join(model_directory, "config.json")
st_pattern = os.path.join(model_directory, "*.safetensors")
model_path = glob.glob(st_pattern)[0]

# Create config, model, tokenizer and generator
config = ExLlamaConfig(model_config_path)               # create config from config.json
config.model_path = model_path                          # supply path to model weights file

# config.set_auto_map("14.00,20.00")
config.set_auto_map('18.8897,18.8897')
config.set_auto_map('22,20')



model = ExLlama(config)                                 # create ExLlama instance and load the weights
tokenizer = ExLlamaTokenizer(tokenizer_path)            # create tokenizer from tokenizer model file

cache = ExLlamaCache(model)                             # create cache for inference
generator = ExLlamaGenerator(model, tokenizer, cache)   # create generator

# Configure generator
generator.disallow_tokens([tokenizer.eos_token_id])
generator.settings.token_repetition_penalty_max = 1.15
generator.settings.temperature = 0.1
generator.settings.top_p = 1.0
# generator.settings.top_k = 100
# generator.settings.typical = 0.5

# Produce a simple generation
system = "Reformat the following transcript into Markdown. Combine multiple contiguous lines from the same speaker into a single block and split into sentences and paragraphs as necessary. Try to fix capitalization, transcription errors, or misattributed speaker labels. Also **bold** the speaker labels. Reply with only the corrected transcript as we will be using your output programmatically."

token_count = 0
chunks = []
chunk = ""
with open("../transcript.txt") as file:
    for line in file:
        # Concatenate the string
        chunk += line

        # Count tokens
        tokens = tokenizer.encode(line)
        token_count += len(tokens[0])
        if token_count >= 1000:
            chunks.append(chunk)
            token_count = 0
            chunk = ""

print(f"### Chunks: {len(chunks)}")

output_file = open("transcript-edited-by-orcaminiv3-70b.txt", "a")
i = 0
for chunk in chunks:
    print(f"### chunk {i}")
    i += 1
    ### Orca Hashes
    # https://huggingface.co/TheBloke/orca_mini_v3_70B-GPTQ#prompt-template-orca-hashes
    input = f"""### System:
{system}

### User:
{chunk}

### Assistant:
"""
    output = generator.generate_simple(input, max_new_tokens = 4000)
    print(output[len(input):])
    output_file.write(output[len(input):])
    output_file.flush()





'''
Debug...

# input = f"<|system|>{system}</s><|prompter|>{user}</s><|assistant|>"

### OpenOrca Platypus2
# https://huggingface.co/Open-Orca/OpenOrca-Platypus2-13B#prompt-template-for-base-platypus2-13b
# https://huggingface.co/Open-Orca/OpenOrcaxOpenChat-Preview2-13B
# input = f"{system}<|end_of_turn|>User: {chunk}<|end_of_turn|>Assistant:"
# Alternative Alpaca Instruct style:
input = f"""### Instruction:

{system}


{chunk}

### Response:
"""

print("## Prompt")
print("```")
print(input)
print("```")
print("## Output")
print("```")
print(output[len(input):])
print("```")
'''
