# pip install transformers torch --upgrade
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def main():
    prompt = "Write a small poem about the ocean"
    model_name = "google/flan-t5-base"   # Better quality than small, but not too heavy

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # Encode the prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate text
    outputs = model.generate(**inputs, max_new_tokens=100)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(result)

if __name__ == "__main__":
    main()
