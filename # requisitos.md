# requisitos
- vou desenvolver uma plataforma que seja capaz de extrair uma tabela de orçamento de um pdf escrito em portugues
- preciso extrair os itens dessa tabela do pdf para construir uma base de dados de referencia para novos itens
- preciso extrair o nome, telefone, email, endereço do cliente, endereço de entrega, e identificação do cliente
- preciso extrair o nome do vendedor(a)
- data de realização do orçamento
- data de expiração do orçamento
- é preciso extrair os valor numéricos 
- é preciso validar se algum valor está incorreto
- é preciso validar se o valor total dos itens está correto
- é precico verificar se há itens duplicados
- alguns itens dizem respeito a material e medidas e largura e comprimento, é necessário criar uma métrica para conseguir utilizar em novos orçamentos
    - por exemplo: tenho o orçamento para a placa de material "m1" de 600x200 cm2 por valor x, e preciso fazer uma estimativa para placa de material "m1" de 350x400 cm2, ou, placa de material "m2" de 600x200 cm2, e assim por diante.

# proposta
- desenvolver uma RAG com gemini capaz de ler arquivo pdf e extrair as informações:
    - resumo do orçamento
    - informações do cliente
    - informações do vendedor(a)
    - itens do orçamento
- cria uma base relacional para salvar os dados do cliente, vendedor, orçamento, itens do orçamento, valor total, datas
- armazenar os documentos processamento
- desenvolver uma plataforma com streamlit como MVP
    - acessar funcionalidades da plataforma inserindo apenas o nome (depois evolui o login)
    - permitir carregar arquivo pdf
    - salvar o arquivo
    - permitir busca de pdf pelo nome do cliente, nome da vendedora, data, status
    - permitir busca nos itens do orçamento que foram criados
    - permitir extração dos dados no formato csv
    - permitir geração/preenchimento de novos orçamentos

# backlog
- login
- desenvolver o pós venda
- acompanhamento da aprovação da proposta do gerente
- acompanhamento de aprovação do orçamento pelo cliente
- realizar assinatura digital
- chat via whatsapp
- geração automática do orçamento utilizando uma llm
- intergração por email
- geração de imagem simulada do resultado
    - inserir objeto e pessoas em escala
    - é possível gerar arquivos para serem utilizados em outras ferramentas (ex: canvas)