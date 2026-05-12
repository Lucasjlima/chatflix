# Chatflix — Design Document

**Data:** 2026-05-12
**Autor:** Lucas (lucasjlima2006@gmail.com)
**Status:** Aprovado para implementação
**Base:** `projeto_filmes.md` (spec original, na raiz do repositório)

---

## 1. Visão geral

Aplicação web minimalista que recomenda **um filme por vez** com base no humor, preferências e características descritas pelo usuário em linguagem natural. Hospedada em **EC2 da AWS**. Construída como projeto de estudo de deploy + integração com IA.

**Stack final:**

- **Linguagem:** Python 3.11+
- **UI:** Streamlit (única camada — sem Flask)
- **IA:** Google Gemini (`google-generativeai`) com `response_schema` para JSON estruturado
- **Metadados:** TMDB API (REST via `requests`)
- **Persistência:** nenhuma — totalmente stateless; memória de sessão vive em `st.session_state`
- **Testes:** pytest + pytest-mock + requests-mock

---

## 2. Arquitetura

### 2.1 Visão de alto nível

Aplicação Streamlit única, stateless por servidor. Estado de uma conversa vive apenas no `st.session_state` do navegador do usuário; some quando a aba fecha. Sem banco, sem cookies persistentes, sem cache compartilhado.

```
                        ┌──────────────────────┐
                        │   Browser (usuário)  │
                        └──────────┬───────────┘
                                   │ HTTP
                        ┌──────────▼───────────┐
                        │  Streamlit (app.py)  │
                        │  Hero centralizado   │
                        └──────────┬───────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
   ┌──────────▼─────────┐  ┌──────▼──────┐  ┌──────────▼─────────┐
   │ services/gemini.py │  │ services/   │  │ services/tmdb.py   │
   │ JSON estruturado:  │  │ recommender │  │ search + details   │
   │ {title,year,       │  │ (orquestra) │  │ poster/sinopse/    │
   │  justification}    │  │             │  │ diretor/imdb/...   │
   └────────┬───────────┘  └─────────────┘  └──────────┬─────────┘
            │                                          │
       Gemini API                              TMDB API (REST)
```

### 2.2 Fluxo numa frase

Usuário digita pedido → `recommender` envia ao Gemini com lista de filmes já sugeridos (do `session_state`) pedindo JSON → recebe `{title, year, justification}` → busca no TMDB pelo título+ano → enriquece com metadados → renderiza card → grava título na lista de "já sugeridos" pra próxima rodada não repetir.

### 2.3 Princípio de isolamento

`app.py` **não importa** `google.generativeai` nem `requests` diretamente. Toda integração externa passa por `services/`. Isso torna o `recommender` substituível (trocar provedor de IA é cirúrgico) e o `app.py` curto (~80-120 linhas).

---

## 3. Estrutura de arquivos

```
chatflix/
├── app.py                      # Streamlit: UI hero + orquestração da sessão
├── config.py                   # Carrega .env, expõe settings tipados, fallbacks
├── services/
│   ├── __init__.py
│   ├── gemini.py               # GeminiClient: prompt + response_schema → Recommendation
│   ├── tmdb.py                 # TMDBClient: search_movie, get_movie_details
│   └── recommender.py          # recommend(prompt, exclude_titles) → MovieCard
├── models.py                   # dataclasses: Recommendation, MovieCard, exceções
├── prompts/
│   └── system.txt              # System prompt (escopo + guardrails + estilo)
├── assets/
│   └── poster_fallback.png     # Imagem padrão quando TMDB não tem poster
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures + monkeypatch de env vars
│   ├── test_gemini.py
│   ├── test_tmdb.py
│   └── test_recommender.py
├── docs/
│   ├── deploy-ec2.md           # Guia detalhado de deploy (systemd / tmux / Docker)
│   └── superpowers/
│       └── specs/
│           └── 2026-05-12-chatflix-design.md   # este documento
├── .env.example                # GEMINI_API_KEY=, TMDB_API_KEY=
├── .gitignore                  # .env, .venv, .superpowers/, __pycache__/
├── requirements.txt            # streamlit, google-generativeai, requests, python-dotenv
├── requirements-dev.txt        # pytest, pytest-mock, requests-mock
├── README.md                   # Setup local + deploy EC2 (resumo)
└── projeto_filmes.md           # Spec original (preservado para histórico)
```

### 3.1 Responsabilidades por módulo

| Módulo | Responsabilidade | Não deve fazer |
|---|---|---|
| `app.py` | Renderizar UI, ler input, chamar `recommender.recommend`, gerenciar `session_state.excluded_titles` | Chamar Gemini/TMDB direto, conhecer schema das APIs |
| `config.py` | Carregar env vars com defaults; expor `settings.gemini_key`, `settings.tmdb_key`, mensagens de fallback | Lógica de negócio |
| `services/gemini.py` | Construir prompt, chamar SDK, validar JSON contra schema, retornar `Recommendation` | Conhecer TMDB; renderizar UI |
| `services/tmdb.py` | `search_movie(title, year)`, `get_movie_details(id)`, normalizar resposta em `MovieCard` | Conhecer Gemini; decidir fallbacks de mensagem ao usuário |
| `services/recommender.py` | Orquestrar: Gemini → TMDB → aplicar fallbacks de campos faltantes → propagar erros tipados | Renderizar; conhecer Streamlit |
| `models.py` | `@dataclass Recommendation`, `MovieCard`, classes de exceção | Lógica |
| `prompts/system.txt` | System prompt versionado (fora do código) | — |
| `tests/` | Cobrir cada service e o `recommender` com mocks | Chamar APIs reais |

---

## 4. Modelos de dados

```python
# models.py

@dataclass(frozen=True)
class Recommendation:           # vem do Gemini
    title: str
    year: int | None
    justification: str          # por que combina com o pedido

@dataclass(frozen=True)
class MovieCard:                # vai para a UI
    title: str
    year: int | None
    poster_url: str | None      # None aciona fallback (assets/poster_fallback.png)
    imdb_rating: str            # "8.4" ou "Não disponível"
    director: str               # ou "Não encontrado"
    synopsis: str               # ou "Sinopse não encontrada"
    genres: list[str]           # vazio → UI omite a linha
    justification: str          # vem do Gemini, repassada
```

### 4.1 Schema do JSON estruturado do Gemini

```python
response_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "year": {"type": ["integer", "null"]},
        "justification": {"type": "string"},
    },
    "required": ["title", "justification"],
}
```

`title == ""` é o sinal de "pedido fora de escopo" — ver §6.

---

## 5. Estado da sessão (Streamlit `session_state`)

| Chave | Tipo | Função |
|---|---|---|
| `excluded_titles` | `list[str]` | Títulos já sugeridos nesta sessão; injetados no prompt para evitar repetição |
| `last_card` | `MovieCard \| None` | Última recomendação renderizada (mantida na tela após "Outra sugestão") |
| `last_prompt` | `str` | Pedido original do usuário (reusado quando ele clica "Outra sugestão") |
| `error` | `str \| None` | Mensagem amigável a renderizar acima do hero |

### 5.1 Regras de transição

- **Submit no input do hero:** reseta `excluded_titles=[]`, salva `last_prompt`, chama `recommender.recommend(prompt, exclude=[])`.
- **Clique em "Outra sugestão":** reusa `last_prompt`, chama `recommender.recommend(last_prompt, exclude=excluded_titles)`.
- **Após resposta bem-sucedida:** `excluded_titles.append(card.title)`, `last_card = card`.
- **Após erro:** `error = e.user_message`, `last_card` permanece (não some o filme anterior só por erro).
- **Teto de exclusão:** `excluded_titles` é truncado para os 20 mais recentes antes de virar prompt. Evita prompt gigante e bloqueio do Gemini por falta de opções.
- **Reload de aba:** tudo zera. Stateless por design.

---

## 6. Fluxo de dados — caminho feliz

```
1. Usuário digita pedido no input do hero e clica "Recomendar filme"
        │
        ▼
2. app.py:
     - session_state.last_prompt = input
     - chama recommender.recommend(prompt, exclude=session_state.excluded_titles)
        │
        ▼
3. recommender.recommend():
     a. gemini.suggest(prompt, exclude_titles)
            - Prompt = system.txt + "Pedido: {prompt}\nNAO sugerir: {exclude_titles}"
            - response_schema força {title, year, justification}
            - retorna Recommendation
            - se rec.title == "" → raise OffTopicRequest
     b. tmdb.search_movie(rec.title, rec.year)
            - se sem resultados: raise MovieNotFound
     c. tmdb.get_movie_details(movie_id)
            - monta MovieCard com fallbacks campo-a-campo
     d. devolve MovieCard
        │
        ▼
4. app.py:
     - session_state.excluded_titles.append(card.title)
     - session_state.last_card = card
     - render_card(card)
```

### 6.1 Decisão importante: validação de escopo é do Gemini, não do Python

Tentar detectar "off-topic" via regex/heurística em Python seria frágil. O `prompts/system.txt` instrui o Gemini a, se o pedido não for sobre filmes, retornar:

```json
{"title": "", "year": null, "justification": "Meu objetivo é apenas recomendar filmes com base nas suas preferências."}
```

`services/gemini.py` detecta `title == ""` e levanta `OffTopicRequest` — não chama TMDB, não consome quota.

---

## 7. Tratamento de erros

### 7.1 Hierarquia de exceções (`models.py`)

```python
class RecommendError(Exception):
    """Base. user_message é texto pronto para o usuário."""
    user_message: str = ""

class MovieNotFound(RecommendError):       # TMDB não tem o filme sugerido
    user_message = "Não foi possível encontrar um filme correspondente."

class AIQuotaExceeded(RecommendError):     # 429 / quota Gemini
    user_message = "Ocorreu um erro nas configurações internas da IA."

class AIInternalError(RecommendError):     # 5xx / JSON inválido / SDK exception
    user_message = "Ocorreu um erro nas configurações internas da IA."

class TMDBError(RecommendError):           # 5xx / timeout TMDB
    user_message = "Ocorreu um erro interno na API."

class OffTopicRequest(RecommendError):     # Gemini devolveu title=""
    user_message = "Meu objetivo é apenas recomendar filmes com base nas suas preferências."
```

### 7.2 Mapeamento camada → exceção

| Camada | Captura | Levanta |
|---|---|---|
| `services/gemini.py` | `google.api_core.exceptions.ResourceExhausted` | `AIQuotaExceeded` |
| `services/gemini.py` | qualquer outra exceção da SDK; falha de validação do JSON | `AIInternalError` |
| `services/gemini.py` | resposta com `title == ""` | `OffTopicRequest` |
| `services/tmdb.py` | `requests.Timeout`, status 5xx | `TMDBError` |
| `services/tmdb.py` | `results == []` em `search_movie` | `MovieNotFound` |
| `services/recommender.py` | não captura — propaga para `app.py` | — |
| `app.py` | `except RecommendError as e:` | `st.session_state.error = e.user_message` |

### 7.3 Fallbacks de campos do `MovieCard` (sem virar exceção)

Quando o TMDB **encontra** o filme mas falta um campo, `services/tmdb.py` aplica fallback campo-a-campo:

| Campo | TMDB ausente | Fallback |
|---|---|---|
| `poster_url` | `poster_path` é `None` | `None` (UI renderiza `assets/poster_fallback.png`) |
| `director` | nenhum crew com `job=="Director"` | `"Não encontrado"` |
| `imdb_rating` | `vote_average == 0` ou `None` | `"Não disponível"` |
| `synopsis` | `overview` vazio/None | `"Sinopse não encontrada"` |
| `genres` | lista vazia | `[]` (UI omite linha) |
| `year` | `release_date` ausente ou inválido | `None` (UI omite ano) |

### 7.4 Timeouts e retries

- **Gemini SDK:** confia no comportamento padrão da SDK `google-generativeai` (timeout interno + retries de rede transitórios, se houver). Sem retry custom no nosso código. `ResourceExhausted` é imediatamente capturado e mapeado para `AIQuotaExceeded` — não tentamos novamente.
- **TMDB (`requests`):** `timeout=5`; **sem retry** — falhou, vira `TMDBError`. Prioriza UX rápida (spec original: "rapidez, carregamento rápido").

### 7.5 Logging

`logging` padrão do Python, nível `INFO`. Loga:

- Prompt do usuário (truncado em 200 chars)
- Título sugerido pelo Gemini
- Latência de cada chamada externa (`gemini`, `tmdb_search`, `tmdb_details`)
- Stack trace de exceções

**Não loga** chaves de API nem PII. (Não há PII coletada de qualquer forma.)

---

## 8. UI / Visual

### 8.1 Layout escolhido

**Hero centralizado** (opção C dos mockups). Dois estados visuais:

- **Vazio (landing):** brand "CHATFLIX" pequeno no topo, título grande gradiente roxo "Que filme você procura?", subtítulo "Descreva clima, humor, atmosfera ou tema", input centralizado, botão "Recomendar filme".
- **Com recomendação:** input mantido visível (menor), card do filme abaixo (poster esquerda + meta/sinopse/justificativa direita), botão "Outra sugestão" ghost embaixo do card.

### 8.2 Design tokens

**Cores — fundo**

| Token | Valor | Uso |
|---|---|---|
| `bg-base` | `#000000` | Fundo da página |
| `bg-surface` | `#0f0a1a` | Cards, inputs |
| `bg-elevated` | `#1a0f2e` | Pills, estados de hover |

**Cores — roxo (acentos)**

| Token | Valor | Uso |
|---|---|---|
| `accent-light` | `#c084fc` | Texto destaque, labels |
| `accent` | `#a855f7` | Brand, links |
| `accent-strong` | `#7c3aed` | Botões, bordas ativas |
| `accent-border` | `#2d1b4e` | Bordas neutras |

**Cores — texto**

| Token | Valor | Uso |
|---|---|---|
| `text-primary` | `#ffffff` | Títulos |
| `text-body` | `#dddddd` | Corpo |
| `text-muted` | `#888888` | Subtítulos, metadados |

### 8.3 Tipografia

- **Família:** Inter (fallback: Segoe UI, system-ui, sans-serif)
- **Hero title:** 32px / 700 / gradient roxo (`linear-gradient(135deg, #c084fc 0%, #7c3aed 100%)`)
- **Card title:** 20px / 700 / branco
- **Body:** 13px / 400 / `#ddd`
- **Meta/muted:** 11px / 400 / `#888`
- **Label uppercase:** 10px / 600 / letter-spacing 2px / `accent-light`

### 8.4 Efeitos

- **border-radius:** 10px (inputs, botões), 14px (cards)
- **Sombra botão primário:** `0 4px 12px rgba(124, 58, 237, 0.35)`
- **Sombra card do filme:** `0 6px 16px rgba(124, 58, 237, 0.25)` no poster
- **Hover botão:** brilho leve (+8% lightness) + sombra expandida
- **Transição:** `180ms ease-out` em hover/focus

### 8.5 Implementação no Streamlit

O tema padrão do Streamlit é limitado para chegar nesse visual. Estratégia:

1. CSS customizado global injetado via `st.markdown("<style>...</style>", unsafe_allow_html=True)` no início de `app.py`
2. Componentes nativos (`st.text_input`, `st.button`) recebem regras CSS que sobrescrevem o tema
3. Card do filme renderizado com HTML direto via `st.markdown` (mais controle sobre layout do que `st.image` + colunas)
4. Imagem do poster via `<img>` HTML para suportar fallback gracioso

---

## 9. Estratégia de testes

### 9.1 Stack

```
pytest
pytest-mock         # mocker fixture
requests-mock       # mock HTTP do TMDB
```

Em `requirements-dev.txt` separado do `requirements.txt` de produção.

### 9.2 Cobertura alvo

| Módulo | Cobertura alvo | Por quê |
|---|---|---|
| `services/gemini.py` | ~90% | Parsing de JSON + mapeamento de exceções |
| `services/tmdb.py` | ~90% | Fallbacks campo-a-campo são fáceis de quebrar silenciosamente |
| `services/recommender.py` | 100% | Orquestração — pequeno e crítico |
| `models.py` | — | Só dataclasses |
| `config.py` | smoke | Um teste de feliz-caminho basta |
| `app.py` | 0% | UI Streamlit, fora de escopo |

### 9.3 Casos de teste

**`tests/test_gemini.py`** (mock do `genai.GenerativeModel`)

- resposta JSON válida → retorna `Recommendation` correto
- resposta com `title == ""` → levanta `OffTopicRequest`
- `ResourceExhausted` da SDK → levanta `AIQuotaExceeded`
- JSON inválido / campo faltando → levanta `AIInternalError`
- exceção genérica da SDK → levanta `AIInternalError`
- prompt inclui `exclude_titles` quando lista não vazia
- prompt **não** menciona exclusão quando lista vazia

**`tests/test_tmdb.py`** (`requests-mock`)

- `search_movie` retorna primeiro match com `title` e `year`
- `search_movie` com `year=None` funciona
- `search_movie` sem resultados → levanta `MovieNotFound`
- `get_movie_details` monta `MovieCard` completo
- fallback: `poster_path=None` → `poster_url=None`
- fallback: nenhum diretor no crew → `"Não encontrado"`
- fallback: `vote_average=0` → `"Não disponível"`
- fallback: `overview=""` → `"Sinopse não encontrada"`
- fallback: `release_date=""` → `year=None`
- `requests.Timeout` → levanta `TMDBError`
- HTTP 500 → levanta `TMDBError`

**`tests/test_recommender.py`** (mocker em `gemini` + `tmdb`)

- caminho feliz: Gemini ok → TMDB ok → retorna `MovieCard`
- propaga `OffTopicRequest` sem chamar TMDB
- propaga `AIQuotaExceeded` sem chamar TMDB
- Gemini ok mas TMDB `MovieNotFound` propaga
- TMDB com erro → propaga `TMDBError`
- passa `exclude_titles` para `gemini.suggest` corretamente

### 9.4 Fixtures (`tests/conftest.py`)

```python
@pytest.fixture(autouse=True)
def fake_env(monkeypatch):
    """Garante que testes nunca usem chaves reais."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("TMDB_API_KEY", "test-key")

@pytest.fixture
def fake_recommendation():
    return Recommendation(title="O Iluminado", year=1980,
                          justification="Atmosfera sombria e lenta.")

@pytest.fixture
def fake_tmdb_search_response():
    return {"results": [{"id": 694, "title": "O Iluminado",
                         "release_date": "1980-05-23"}]}

@pytest.fixture
def fake_tmdb_details_response():
    """JSON realista de /movie/{id}?append_to_response=credits.
    Inclui poster_path, overview, vote_average, release_date, genres,
    e credits.crew com pelo menos um item job=='Director'."""
    return {
        "id": 694,
        "title": "O Iluminado",
        "release_date": "1980-05-23",
        "poster_path": "/abc123.jpg",
        "overview": "Um escritor aceita ser zelador de um hotel isolado...",
        "vote_average": 8.4,
        "genres": [{"id": 27, "name": "Terror"}, {"id": 53, "name": "Suspense"}],
        "credits": {
            "crew": [
                {"job": "Director", "name": "Stanley Kubrick"},
                {"job": "Writer", "name": "Stephen King"},
            ]
        },
    }
```

### 9.5 Convenções

- **Sem chamadas de rede reais.** Fixture `autouse` injeta chaves fake.
- **Naming:** `test_<funcao>_<condicao>_<resultado>` — ex: `test_search_movie_no_results_raises_movie_not_found`.
- **Um assert principal por teste** (testes de fallback podem agrupar asserts por campo).
- **Comando:** `pytest` na raiz, sem flags.

### 9.6 O que NÃO é testado

- **A IA em si.** Não-determinística, sem ROI.
- **TMDB API real.** Confiamos no contrato documentado.
- **Streamlit UI.** Frágil, baixo ROI. Validação manual no browser cobre.

---

## 10. Configuração e segredos

### 10.1 `.env` (local) — não commitar

```
GEMINI_API_KEY=...
TMDB_API_KEY=...
```

### 10.2 `.env.example` (commitado)

```
GEMINI_API_KEY=
TMDB_API_KEY=
```

### 10.3 Provisionamento

| Chave | Onde obter | Custo |
|---|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey | Gratuito (free tier generoso) |
| `TMDB_API_KEY` | https://www.themoviedb.org/settings/api | Gratuito |

### 10.4 No EC2

`.env` no diretório do projeto, `chmod 600 .env`. **Nunca** commitado. Sem AWS Secrets Manager / Parameter Store no MVP (over-engineering para o escopo de estudo).

---

## 11. Deploy na EC2

### 11.1 Pré-requisitos comuns

- **Instância:** `t3.micro` ou `t3.small` (free tier elegível), Amazon Linux 2023 ou Ubuntu 22.04
- **Security Group:** inbound TCP **8501** (porta padrão Streamlit) liberado para `0.0.0.0/0` ou IP específico
- **IAM role:** nenhuma necessária (não usamos serviços AWS no código)
- **Python:** 3.11+ (Amazon Linux 2023 vem com 3.9; instalar 3.11 via `dnf install python3.11`)
- **Acesso:** `http://<EC2_PUBLIC_IP>:8501`

### 11.2 Três opções documentadas (decisão adiada para o momento do deploy)

| Opção | Quando faz sentido | Pegadinhas principais |
|---|---|---|
| **systemd service** | Mostrar DevOps no portfólio; reboot survival; logs estruturados via journalctl | Path do `python` precisa ser o do venv; `User=` não pode ser `root`; `WorkingDirectory=` precisa apontar pro repo |
| **tmux/screen** | Validar rápido sem cerimônia | Não sobrevive a reboot; logs ficam dentro do tmux |
| **Docker** | Paridade com ambiente local; portátil | Build leva ~3min; espaço extra em disco; `--restart=always` no `docker run` |

`docs/deploy-ec2.md` vai cobrir as três com passo-a-passo completo.

### 11.3 HTTPS / domínio

**Fora de escopo do MVP.** Acesso via HTTP na porta 8501. Próximo passo (documentado como "future work"): Caddy ou nginx + Let's Encrypt na frente do Streamlit.

---

## 12. Versionamento (GitHub)

Conforme spec original:

1. `git init` no diretório
2. `.gitignore` com `.env`, `.venv/`, `__pycache__/`, `.superpowers/`, `*.pyc`
3. Criar repo `Lucasjlima/chatflix` via `mcp__github__create_repository`
4. Primeiro commit: `"Initial project setup for chatflix app"`
5. `git remote add origin https://github.com/Lucasjlima/chatflix.git`
6. `git branch -M main && git push -u origin main`

Confirmar quem está autenticado no MCP GitHub antes do push; pedir confirmação ao usuário se não for `Lucasjlima`.

---

## 13. Escopo explícito

### 13.1 Fora do MVP

| Item | Por quê |
|---|---|
| Flask | Streamlit cobre UI + lógica; desvio consciente do spec original |
| RAG / dataset Netflix Kaggle | Decidido manter simples; spec original já marcava como "possível" |
| Banco de dados | Spec exige stateless; `session_state` cobre memória em sessão |
| Autenticação / contas | Spec exige stateless e sem persistência |
| HTTPS / domínio próprio | Próximo passo pós-MVP |
| CI/CD | `pytest` local basta para escopo de aprendizado |
| Internacionalização | Português hardcoded — público-alvo é o autor |
| Mobile-first / responsivo profundo | Streamlit já é responsivo razoável |
| Cache de respostas Gemini/TMDB | Stateless por spec; sem necessidade de performance no uso pessoal |
| Rate limiting na aplicação | Quotas das APIs já limitam |

### 13.2 Desvios conscientes do `projeto_filmes.md` original

| Item no spec original | Decisão | Por quê |
|---|---|---|
| "Stack Principal: Python, Streamlit, Flask" | **Flask removido** | Redundante com Streamlit; aprovada Opção 1 (Streamlit puro) |
| "Dataset Kaggle Netflix" + "possível RAG" | **Removido** | Marcado como "possível" no spec; escolhido "sem RAG, manter simples" |
| Provedor de IA não especificado | **Google Gemini** | Decisão do usuário; free tier ajuda no estudo |

---

## 14. Performance esperada

- **Latência:** 2-5s por recomendação (Gemini ~1-3s + TMDB ~200-500ms × 2 chamadas)
- **Sem cache** — cada submit é uma rodada completa de API. Para uso pessoal/portfólio, OK.
- **`t3.micro` aguenta:** Streamlit consome ~150MB RAM idle; instância free tier (1GB) tem folga.

---

## 15. Critérios de aceite do MVP

1. Usuário acessa a aplicação no navegador e vê o hero centralizado com input.
2. Usuário descreve um pedido em linguagem natural e clica "Recomendar filme".
3. Em até ~5s, recebe um card com poster, título, ano, diretor, nota IMDB, gêneros, sinopse e justificativa.
4. Clicar "Outra sugestão" retorna um filme diferente para o mesmo pedido.
5. Pergunta fora de escopo (ex: "qual a capital da França?") recebe a mensagem de fallback definida no spec.
6. Erros (filme não achado, quota excedida, falha de API) mostram a mensagem amigável correta sem quebrar a UI.
7. Recarregar a página zera a sessão (stateless).
8. Aplicação acessível via `http://<EC2_PUBLIC_IP>:8501` após deploy.
9. `pytest` na raiz roda todos os testes verdes.

---

## 16. Próximos passos imediatos

1. Revisão deste documento pelo usuário.
2. Após aprovação, invocar a skill `writing-plans` para gerar o plano detalhado de implementação (ordem de criação dos arquivos, marcos de validação).
3. Implementação seguindo o plano.
4. Inicialização do repositório GitHub e push.
5. Deploy na EC2 (opção a ser escolhida pelo usuário no momento).
