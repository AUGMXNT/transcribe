#!/usr/bin/env python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import BitsAndBytesConfig

tokenizer = AutoTokenizer.from_pretrained("togethercomputer/LLaMA-2-7B-32K")

double_quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

# model = AutoModelForCausalLM.from_pretrained("togethercomputer/LLaMA-2-7B-32K", trust_remote_code=True, torch_dtype=torch.float16)
# Flash Attention 2 barfing
model = AutoModelForCausalLM.from_pretrained("togethercomputer/LLaMA-2-7B-32K", trust_remote_code=False, torch_dtype=torch.float16)
# model = AutoModelForCausalLM.from_pretrained("togethercomputer/LLaMA-2-7B-32K", trust_remote_code=False, torch_dtype=torch.bfloat16, quantization_config=double_quant_config)


filename = "transcript.txt"
with open(filename, 'r') as file:
    text = file.read()

input_context = f"""<s>[INST] <<SYS>>
Reformat this transcript into markdown paragraphs and sentences and bold the speakers tags. Try to fix capitalization or transcription errors and make light edits such as removing ums, etc.
<</SYS>>

{text} [/INST]"""

input_ids = tokenizer.encode(input_context, return_tensors="pt")
output = model.generate(input_ids, 
                        max_length=12000, 
                        temperature=0.1)
output_text = tokenizer.decode(output[0], skip_special_tokens=True)

out_file = "transcript-edited.txt"
with open(out_file, 'w') as file:
    file.write(output_text)
