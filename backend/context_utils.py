def extract_best_sentence(context, question):

    sentences = context.split(".")
    question_words = question.lower().split()

    best_sentence = ""
    best_score = 0

    for s in sentences:
        score = sum(1 for w in question_words if w in s.lower())

        if score > best_score:
            best_score = score
            best_sentence = s

    return best_sentence.strip()