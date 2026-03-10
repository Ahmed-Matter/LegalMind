from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="google/flan-t5-base"
)

def generate_answer(prompt):

    result = generator(
        prompt,
        max_length=200,
        do_sample=False
    )

    return result[0]["generated_text"]