from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

PROMPT = "Explain how rainbows are formed"
MODEL = "google/flan-t5-large"  # large model, runs locally

def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)

    inputs = tokenizer(PROMPT, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=150)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(response)

if __name__ == "__main__":
    main()
