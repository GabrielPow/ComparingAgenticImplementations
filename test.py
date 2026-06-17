from transformers import pipeline

pipe = pipeline("text-generation", model="google/gemma-2b")
output = pipe("Once upon a time,")[0]["generated_text"]
print(output)