from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

MODEL_NAME = "google/flan-t5-large"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# keep prompts short for stability
MAX_PROMPT_CHARS = 700


def clean_text(text: str):
    """
    Remove repeated words and duplicated phrases.
    """

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    # remove duplicated consecutive words
    words = text.split()
    cleaned_words = []

    for w in words:
        if not cleaned_words or cleaned_words[-1].lower() != w.lower():
            cleaned_words.append(w)

    text = " ".join(cleaned_words)

    # remove repeated short phrases
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text, flags=re.IGNORECASE)

    return text.strip()


def generate_answer(prompt: str):

    # prevent very long prompts
    if len(prompt) > MAX_PROMPT_CHARS:
        prompt = prompt[:MAX_PROMPT_CHARS]

    try:

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        outputs = model.generate(
            **inputs,
            max_new_tokens=60,
            num_beams=4,
            no_repeat_ngram_size=3,
            repetition_penalty=1.3,
            length_penalty=1.0,
            early_stopping=True
        )

        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        text = clean_text(text)

        return text

    except Exception as e:
        print("LLM ERROR:", e)
        return "I could not generate a response."