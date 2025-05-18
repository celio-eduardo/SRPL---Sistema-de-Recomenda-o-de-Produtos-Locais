# Documentação do Sistema de Recomendação de Produtos Locais

## Visão Geral

Este sistema foi desenvolvido para conectar pequenos produtores a consumidores locais, proporcionando acesso a produtos mais frescos, locais e de acordo com preferências e sazonalidades. O sistema utiliza técnicas de recomendação baseadas em:

1. Filtro de distância
2. Preferências do usuário
3. Sazonalidade dos produtos
4. Filtragem colaborativa com revisões e pontuações

## Funcionalidades Implementadas

### 1. Interface Web com Flask e Mapa Interativo
- Aplicação web responsiva desenvolvida com Flask
- Mapa interativo utilizando Leaflet.js para visualização geoespacial
- Marcadores para localização do usuário e associações de produtores

### 2. Filtro de Sazonalidade dos Produtos
- Implementação de modelo de dados com informações de disponibilidade mensal
- Interface para filtrar produtos por mês de disponibilidade
- Integração da sazonalidade no sistema de recomendação

### 3. Sistema de Revisões e Filtragem Colaborativa
- Modelo de dados para armazenar avaliações de usuários
- Interface para avaliação de produtos (1-5 estrelas e comentários)
- Algoritmo de recomendação que considera avaliações, distância e preferências

## Estrutura do Projeto

```
projeto_recomendacao/
├── data/
│   ├── regioes_com_coordenadas.csv
│   └── associacoes_formatadas.csv
├── src/
│   ├── models/
│   │   ├── associacao.py
│   │   ├── produto.py
│   │   └── usuario.py
│   ├── routes/
│   │   └── main.py
│   ├── static/
│   │   └── index.html
│   └── main.py
├── venv/
└── requirements.txt
```

## Tecnologias Utilizadas

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Mapa**: Leaflet.js
- **Dados**: Pandas, GeoPy
- **Visualização**: Folium (opcional para visualizações adicionais)

## Instalação e Execução

1. Clone o repositório ou extraia os arquivos
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```
   python -m src.main
   ```
4. Acesse a aplicação no navegador:
   ```
   http://localhost:5000
   ```

## Uso do Sistema

### Mapa Interativo
- O mapa exibe a localização do usuário e as associações próximas
- Clique nos marcadores para ver detalhes e acessar produtos

### Filtros
- Selecione o mês para ver produtos disponíveis naquele período
- Marque a opção "Apenas Produtos Orgânicos" para filtrar
- Selecione uma associação específica no dropdown

### Avaliações
- Clique no botão "Avaliar" em qualquer produto
- Atribua uma pontuação de 1 a 5 estrelas
- Adicione um comentário opcional
- Envie sua avaliação para melhorar as recomendações

### Recomendações Personalizadas
- O sistema exibe recomendações baseadas em:
  - Distância até as associações
  - Sazonalidade dos produtos
  - Avaliações de outros usuários
  - Preferências (orgânicos, etc.)

## Extensões Futuras

- Integração com banco de dados persistente
- Autenticação de usuários
- Perfis de preferências mais detalhados
- Análise avançada de sazonalidade com dados históricos
- Integração com sistemas de pedidos e entregas

## Referências

- USDA Farmers Markets Directory: https://www.ams.usda.gov/local-food-directories/farmersmarkets
- Open Food Data: https://www.data.gov/food/
- Associações de Produtores Rurais do DF (conforme documentação do projeto)
