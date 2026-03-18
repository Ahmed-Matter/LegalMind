def build_context(chunks,max_chunks=5):
    """build structured context for the LLM"""
    select_chunks=chunks[:max_chunks]

    context_parts=[]

    for i, chunk in enumerate(select_chunks):

        source= chunk.get("source", "Unkown Source")
        text= chunk.get("text","")

        context_parts.append(f"Source {i+1}: {source}\n{text}")
        #context_parts.append(f"Source {i+1}: {source}\n{text}")

        context="\n\n".join(context_parts)

        return context