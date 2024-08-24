# 1. Add tokenizer kind to model details

- One of 3 options, Tiktoken-100K, Tiktoken-200K (as in GPT-4o), LLama 3
- When calculating tokens in new chat and dialog windows use the corresponding token
- Make sure adding a new field doesn't break existing encrypted and stored on the disk (as pickle) models, defaul to Tiktoken-100K

# In dialog window add performance metrics

- Time-to-first token
- Tokens per second (excluding the time to the first token)