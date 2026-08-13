import os
from groq import Groq


def generate_answer(query: str, context_chunks: list[dict], api_key: str = None) -> str:
    """Generates an answer with Groq API based on retrieved context chunks."""
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        return "Error: Groq API key is missing."

    client = Groq(api_key=key)

    # Format retrieved context
    formatted_context = ""
    for idx, chunk in enumerate(context_chunks, 1):
        source = chunk["metadata"].get("source", "Unknown")
        page = chunk["metadata"].get("page", "N/A")
        formatted_context += f"\n--- Context Chunk {idx} (Source: {source}, Page: {page}) ---\n{chunk['text']}\n"

    system_prompt = (
        "You are an expert AI research assistant. Answer the user query using ONLY the provided context passages. "
        "Include precise inline citations like [Source: filename, Page: X] where appropriate. "
        "If the answer cannot be determined from context, state clearly that information is missing."
    )

    user_prompt = f"Context Passages:\n{formatted_context}\n\nUser Question: {query}"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"