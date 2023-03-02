import os

import nltk
import openai
from transformers import GPT2TokenizerFast

nltk.download("punkt")
from nltk.tokenize import word_tokenize

OPENAI_MAX_TOKENS = 4097


def break_up_text(tokens, chunk_size, overlap_size):
    if len(tokens) <= chunk_size:
        yield tokens
    else:
        chunk = tokens[:chunk_size]

        yield chunk
        yield from break_up_text(
            tokens[chunk_size - overlap_size :], chunk_size, overlap_size
        )


def break_up_text_to_chunks(text, chunk_size=4000, overlap_size=100):
    tokens = word_tokenize(text)
    return list(break_up_text(tokens, chunk_size, overlap_size))


def break_up_text_to_max_tokens(text, max_tokens=4000):
    lines = break_up_text_to_chunks(text, chunk_size=max_tokens)

    if lines:
        return convert_to_detokenized_text(lines[0])
    else:
        return text


def convert_to_detokenized_text(tokenized_text):
    prompt_text = " ".join(tokenized_text)
    detokenized_text = prompt_text.replace(" 's", "'s")
    return detokenized_text


def openai_number_of_tokens(text):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    encoded = tokenizer.encode(text)
    # decoded = tokenizer.decode(encoded)
    return len(encoded)


def openai_call(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    openai_tokens = openai_number_of_tokens(prompt)
    openai_remain_tokens = OPENAI_MAX_TOKENS - openai_tokens

    openai_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        n=1,
        stop=None,
        temperature=0,
        max_tokens=openai_remain_tokens,
    )

    if openai_response.choices:
        return openai_response.choices[0].text.strip()

    return None
