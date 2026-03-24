from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

MODEL_NAME = "google/flan-t5-large"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

MAX_PROMPT_CHARS = 1500


def clean_text(text: str):
    """
    Remove repeated words and duplicated phrases.
    """

    text = re.sub(r"\s+", " ", text)

    words = text.split()
    cleaned_words = []

    for w in words:
        if not cleaned_words or cleaned_words[-1].lower() != w.lower():
            cleaned_words.append(w)

    text = " ".join(cleaned_words)

    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text, flags=re.IGNORECASE)

    return text.strip()


def generate_answer(prompt: str):

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
            max_new_tokens=200,
            num_beams=1,
            do_sample=False,
            temperature=0.0,
            no_repeat_ngram_size=2,
            repetition_penalty=1.2,
            length_penalty=1.1,
            early_stopping=True
        )

        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        text = clean_text(text)

        return text

    except Exception as e:
        print("LLM ERROR:", e)
        return "I could not generate a response."