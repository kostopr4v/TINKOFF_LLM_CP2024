
**Команда: "сомнительно, но окей"** <br />
**Цифровой прорыв 2024 31.05-02.06** <br />
**Кейс: "Разработка QnA бота Тинькофф Помощь – Бизнес"**

# ИСПОЛЬЗОВАНИЕ НАШЕГО АПИ <br /> 
https://evident-jolly-primate.ngrok-free.app/assist <br />
**ПРИМЕР ЗАПРОСА** <br />
curl -X POST -H "Content-Type: application/json" -d '{"query": "Как выпустить бизнес-карту?"}' https://evident-jolly-primate.ngrok-free.app/assist <br />

# ФАЙЛЫ
1. train.ipynb - код обучения модели 
2. interact_llama3_llamacpp.py - файл инференса модели 
3. requirements.txt - нужные библиотеки для инференса
4. api - папка для поднятия сервера FastAPI
5. бот - папка с телеграм ботом
*https://huggingface.co/artemgoncarov/saiga_llama_8b_tinkoff/* - ссылка на модельку 3 эпохи ( скачивайте ггуф формат модельки)

# КАК ЗАПУСТИТЬ АПИ
1. Скачивайте папку апи( модельку кладете в ту же папку)
2. Инсталлите все что нужно (скачиваете ngrok)
    1. pip install spacy uvicorn
    2. py -m spacy download ru_core_news_lg
3. Открываете консоль в папке и пишите:
    1. py -m llama_cpp.server --model model-unsloth.Q4_K_M.gguf
    2. py -m llama_cpp.server --model model-unsloth.Q4_K_M.gguf
    3. uvicorn main:app --reload --port 1488
    4. ngrok http http://localhost:1488
4. Пример запроса
  curl -X POST -H "Content-Type: application/json" -d '{"query": "Кто может выпустить бизнес-карту?"}' https://d77f-77-34-223-214.ngrok-free.app/assist ( вместо https://d77f-77-34-223-214.ngrok-free.app указываете вашу ссылку ngrok)

# СОСТАВ КОМАНДЫ
1) Сигалов Константин
2) Беляев Матвей
3) Гончаров Артем
