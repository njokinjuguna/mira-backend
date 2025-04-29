from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load the Hugging Face model and tokenizer once
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

def answer_general_question(question: str) -> str:
    try:
        prompt = f"Answer this interior design question clearly and helpfully: {question}"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = model.generate(**inputs, max_new_tokens=200)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer
    except Exception as e:
        return f"❌ Error from Mira AI: {e}"
