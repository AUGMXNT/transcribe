#!/usr/bin/env python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import BitsAndBytesConfig

tokenizer = AutoTokenizer.from_pretrained("togethercomputer/LLaMA-2-7B-32K")

MODEL_PATH = "syzymon/long_llama_3b_instruct"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True, 
    device_map='cuda',
    torch_dtype=torch.bfloat16,
    mem_attention_grouping=(1, 2048),
)
model.eval()

filename = "transcript.txt"
with open(filename, 'r') as file:
    text = file.read()


prompt = "Reformat the following transcript into markdown paragraphs and sentences and bold the speakers tags. Try to fix capitalization or transcription errors and make light edits such as removing ums, etc.\n\n"

prompt += text + "\n\n"

input_ids = tokenizer(prompt, return_tensors="pt").input_ids
input_ids = input_ids.to(model.device)

outputs = model(input_ids=input_ids)

outputs = model.generate(
    input_ids=input_ids,
    max_new_tokens=8192,
    num_beams=1,
    last_context_length=8192,
    do_sample=True,
    temperature=0.1,
)
output_text = tokenizer.decode(output[0], skip_special_tokens=True)

print(output_text)
import sys
sys.exit()
'''
input_ids = tokenizer.encode(input_context, return_tensors="pt")
output = model.generate(input_ids, 
                        max_length=12000, 
                        temperature=0.1)
'''

out_file = "transcript-edited.md"
with open(out_file, 'w') as file:
    file.write(output_text)
