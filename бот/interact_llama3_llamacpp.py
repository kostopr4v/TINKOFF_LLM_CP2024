import fire
from llama_cpp import Llama

SYSTEM_PROMPT = "Ты — ассистент, который поможет новым и текущим пользователям (предпринимателям) получать моментальные(синхронные) ответы на типовые вопросы про регистрацию бизнеса, кредиты для бизнеса, бизнес-решения, бухгалтерия, продажи, госзакупки, самозанятость, выплаты, инвестиции для бизнеса, основываясь на базе знаний «Тинькофф Помощь. Бизнес», при каждом ответе, ты должен предоставлять ссылку на карточку с похожим запросом."

model = Llama(
    model_path='model-unsloth.Q4_K_M.gguf',
    n_ctx=8192,
    n_parts=1,
    verbose=True,
)


def interact(
    messages,
    top_k=30,
    top_p=0.9,
    temperature=0.4,
    repeat_penalty=1.1,
):
    s = ''
    for part in model.create_chat_completion(
        messages,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
        stream=True,
    ):
        delta = part["choices"][0]["delta"]
        if "content" in delta:
            print(delta["content"], end="", flush=True)
            s += delta["content"]
    
    return s