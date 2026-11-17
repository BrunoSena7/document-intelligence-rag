# Guia de demonstração — API de pedidos (dados fictícios)

> Documento sintético criado exclusivamente para testar o fluxo de RAG. Não representa um sistema ou empresa real.

## Autenticação

A API de pedidos utiliza autenticação por token Bearer. O cliente deve enviar o cabeçalho `Authorization: Bearer <token>` em cada requisição protegida. Tokens expirados devem receber resposta HTTP 401.

## Limite de requisições

O ambiente de demonstração permite até 100 requisições por minuto por token. Ao ultrapassar o limite, a API retorna HTTP 429 e informa o tempo recomendado para tentar novamente.

## Criação de pedidos

Para criar um pedido, envie `POST /orders` com `customer_id` e uma lista de itens contendo `product_id` e `quantity`. A API valida a existência dos produtos e calcula o total no servidor. O cliente não deve enviar o valor final como fonte de verdade.

## Estados do pedido

Um pedido pode estar em `created`, `confirmed`, `preparing`, `ready`, `delivered` ou `cancelled`. As transições são registradas com data e hora. Um pedido cancelado não pode voltar para o fluxo de preparação.

## Persistência

Os dados do ambiente de demonstração são armazenados em PostgreSQL. Backups são realizados diariamente e a restauração deve ser testada antes de qualquer atualização de versão.

## Observabilidade

A API registra identificador de requisição, rota, status HTTP e duração. Tokens, senhas e dados pessoais não devem aparecer nos logs.
