from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_ID = "tabularisai/multilingual-sentiment-analysis"

def main():
    print("=== Using Transformers pipeline ===")
    clf = pipeline("sentiment-analysis", model=MODEL_ID)
    test_texts = [
        "I love this phone!",
        "This is the worst service I have ever experienced."
    ]
    results = clf(test_texts)
    for t, r in zip(test_texts, results):
        print(f'"{t}" -> {r["label"]} (score={r["score"]:.4f})')

    print("\n=== Using tokenizer + model ===")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)

    enc = tokenizer(test_texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**enc)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        labels = ["NEGATIVE", "POSITIVE"]
        for i, t in enumerate(test_texts):
            label = labels[int(probs[i][1] > probs[i][0])]
            score = probs[i].max().item()
            print(f'"{t}" -> {label} (score={score:.4f})')

if __name__ == "__main__":
    main()
