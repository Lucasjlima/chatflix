# Projeto AWS EC2 + IA — Recomendador Inteligente de Filmes

## Objetivo do Projeto

Desenvolver uma aplicação web simples e minimalista utilizando **Python**, **Streamlit**, **Flask** e integração com **IA**, hospedada em uma instância **EC2 da AWS**.

O objetivo principal da aplicação é recomendar filmes de forma inteligente com base no humor, preferências e características fornecidas pelo usuário.

A IA deve atuar exclusivamente como uma recomendadora de filmes.

---

# Contexto da Aplicação

O usuário acessa a aplicação e descreve o tipo de filme que deseja assistir, por exemplo:

- clima emocional
- gênero
- estilo narrativo
- intensidade
- humor
- tema
- época
- características específicas

Exemplo:

> "Quero um filme de suspense psicológico, lento, com plot twist e atmosfera sombria."

A IA deve:

1. Interpretar a intenção do usuário.
2. Recomendar apenas **um único filme por vez**.
3. Explicar por que aquele filme se encaixa na solicitação.
4. Perguntar ao usuário se deseja outra sugestão.
5. Caso o usuário aceite, recomendar outro filme diferente.

---

# Objetivo da IA

A IA deve responder exclusivamente perguntas relacionadas a:

- recomendações de filmes
- análise de preferências cinematográficas
- sugestões baseadas em humor e características

A IA NÃO deve:

- responder perguntas genéricas
- responder perguntas técnicas
- responder dúvidas fora do contexto cinematográfico
- atuar como chatbot geral

Caso o usuário envie algo fora do escopo, a IA deve responder:

> "Meu objetivo é apenas recomendar filmes com base nas suas preferências."

---

# UX / UI Requirements

## Identidade Visual

### Cores predominantes

- Fundo principal: preto
- Elementos principais: roxo
- Texto padrão: branco

### Estilo

A interface deve transmitir:

- modernidade
- minimalismo
- sensação futurista
- simplicidade de uso
- resposta rápida

---

# Estrutura da Página

A aplicação deve possuir apenas:

- uma única página
- sem múltiplas rotas
- sem navegação complexa
- fluxo rápido e direto

Fluxo esperado:

1. Usuário entra
2. Digita o que deseja assistir
3. Recebe recomendação
4. Vai embora

---

# Componentes da Interface

## Chat da IA

A caixa de conversa deve:

- possuir design moderno e minimalista
- utilizar tons de preto e roxo
- possuir texto branco
- crescer dinamicamente conforme a resposta da IA
- ter espaçamento confortável
- possuir boa legibilidade

---

## Botões

Os botões devem:

- possuir cor roxa
- ter hover moderno e perceptível
- transmitir sensação de clique/interatividade
- possuir transições suaves

Exemplo esperado:

- brilho leve
- alteração de sombra
- pequena animação
- mudança de tonalidade

---

# Resposta da IA

A resposta da IA deve exibir:

## Informações do Filme

- capa/poster do filme
- título
- nota IMDB
- diretor
- sinopse
- ano
- gênero
- justificativa da recomendação

---

## Estrutura Esperada da Resposta

A IA deve explicar:

- por que o filme combina com o pedido
- quais elementos conectam com o humor do usuário
- qual atmosfera o filme entrega

---

# Dados e APIs

## TMDB API

Utilizar:

[TMDB API](https://www.themoviedb.org/?utm_source=chatgpt.com)

Objetivo:

- obter capas dos filmes
- metadados
- sinopse
- diretor
- avaliações
- informações gerais

---

## Dataset Kaggle Netflix

Utilizar dataset da Netflix disponível no Kaggle para:

- criação de base interna
- consultas locais
- possível implementação de RAG
- enriquecimento de recomendações

Objetivo do RAG:

- melhorar relevância das recomendações
- reduzir dependência exclusiva da API externa
- facilitar consultas semânticas

---

# Requisitos Técnicos

## Stack Principal

- Python
- Streamlit
- Flask

---

# Arquitetura Esperada

## Backend

Responsável por:

- integração com IA
- tratamento de prompts
- consulta de filmes
- integração com TMDB
- lógica de recomendação
- tratamento de erros

---

## Frontend

Responsável por:

- interface Streamlit
- exibição da conversa
- renderização da resposta
- exibição do poster
- experiência do usuário

---

# Persistência

## Banco de Dados

NÃO utilizar banco de dados.

Nenhuma informação deve ser salva:

- histórico
- prompts
- usuários
- sessões
- recomendações

A aplicação deve ser totalmente stateless.

---

# Edge Cases

## Filme não encontrado

Caso o filme não seja encontrado:

- lançar exceção 404
- exibir mensagem amigável ao usuário

Exemplo:

> "Não foi possível encontrar um filme correspondente."

---

## Perguntas fora do contexto

Caso o usuário faça perguntas não relacionadas a filmes:

Responder:

> "Meu objetivo é apenas recomendar filmes com base nas suas preferências."

---

## Limite da IA excedido

Caso a IA não responda por limite de uso:

Exibir:

> "Ocorreu um erro nas configurações internas da IA."

---

## Erro interno de API

Caso ocorra erro na API:

Exibir:

> "Ocorreu um erro interno na API."

---

## Dados incompletos do filme

Caso algum campo esteja ausente:

- exibir fallback padrão
- nunca quebrar a interface

Exemplos:

| Campo | Fallback |
|---|---|
| imagem | imagem padrão |
| diretor | "Não encontrado" |
| nota | "Não disponível" |
| sinopse | "Sinopse não encontrada" |

---

# Requisitos de Performance

A aplicação deve priorizar:

- rapidez
- simplicidade
- baixo consumo de recursos
- carregamento rápido
- experiência fluida

---

# Objetivo Final

Construir uma aplicação simples, moderna e funcional para estudo de:

- AWS EC2
- Deploy de aplicações Python
- Integração com IA
- Streamlit
- APIs externas
- RAG
- UX minimalista
- Arquitetura backend simples

O foco principal do projeto é aprendizado e prática de deploy + integração de IA em ambiente cloud.

## GitHub MCP and Versioning Instructions

Use the GitHub MCP to version this project directly in the following repository:


The repository don't exists, you need create one.

After creating the project files locally, configure the remote repository and push the initial version using:

```bash
git remote add origin https://github.com/Lucasjlima/chatflix.git
git branch -M main
git push -u origin main
```

Claude should use the GitHub MCP whenever possible to:

- Inspect the repository
- Create or update project files
- Commit the generated code
- Push changes to the `main` branch
- Keep the project versioned during development

Before pushing, make sure the project contains all required files, runs locally, and has a clear initial commit message, such as:

```bash
git add .
git commit -m "Initial project setup for chatflix app"
```