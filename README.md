# Chatflix

Recomendador inteligente de filmes via **Google Gemini** + **TMDB**, com interface Streamlit minimalista (roxo/preto/branco). Projeto de estudo de deploy em AWS EC2.

## Stack

- Python 3.11+
- Streamlit (UI)
- google-generativeai (Gemini)
- requests (TMDB)
- pytest (testes)

## Setup local

1. Clone o repositório e entre na pasta.

2. Crie um ambiente virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Linux/Mac: `source .venv/bin/activate`

3. Instale dependências:

   ```bash
   pip install -r requirements-dev.txt
   ```

4. Copie `.env.example` para `.env` e preencha:

   ```
   GEMINI_API_KEY=sua-chave-do-google-ai-studio
   TMDB_API_KEY=sua-chave-do-tmdb
   ```

   - Gemini: https://aistudio.google.com/apikey (gratuito)
   - TMDB: https://www.themoviedb.org/settings/api (gratuito)

5. Rode:

   ```bash
   streamlit run app.py
   ```

   Abrir http://localhost:8501

## Testes

```bash
pytest
```

Os testes usam mocks (não fazem chamadas reais ao Gemini/TMDB).

## Deploy

Veja [`docs/deploy-ec2.md`](docs/deploy-ec2.md) para guia de deploy em EC2 (systemd, tmux ou Docker).

## Documentação

- Design: [`docs/superpowers/specs/2026-05-12-chatflix-design.md`](docs/superpowers/specs/2026-05-12-chatflix-design.md)
- Plano de implementação: [`docs/superpowers/plans/2026-05-12-chatflix.md`](docs/superpowers/plans/2026-05-12-chatflix.md)
- Spec original (PT-BR): [`projeto_filmes.md`](projeto_filmes.md)

## Licença

Estudo pessoal. Sem licença atribuída.
