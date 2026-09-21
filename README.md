# Spotify Explorer

Aplicação web para explorar e analisar um catálogo de 89.740 músicas, construída sobre um banco relacional MySQL normalizado até a 3FN. O projeto cobre o ciclo completo: modelagem conceitual, ETL de um dataset bruto do Kaggle, API REST em Flask, interface em React e deploy das três camadas na nuvem.

Desenvolvido como trabalho final da disciplina de Banco de Dados I do Bacharelado em Ciência da Computação (UFRJ).

<p align="center">
  <img src="./app_screenshots/index_musics.png" alt="Tela principal do Spotify Explorer" width="100%">
</p>

---

## Acesso

| Camada | Link |
| --- | --- |
| Interface web | https://spotify-frontend-09cs.onrender.com/ |
| API REST | https://pf-2026-1-bd-spotify.onrender.com |
| Banco de dados | Instância MySQL gerenciada na Aiven |

> **Nota sobre a demo:** o banco está em plano gratuito da Aiven e hiberna após períodos de inatividade. Se a interface carregar sem dados, a instância precisa ser reativada. As capturas de tela abaixo mostram a aplicação em funcionamento, e as instruções de execução local permitem rodar o projeto por completo com o dump do banco incluído no repositório.

---

## O problema

O *Spotify Tracks Dataset* é distribuído como um único CSV desnormalizado de 114.000 linhas. Cada linha repete o nome do álbum, do gênero e dos artistas, e o campo `artists` agrupa vários artistas em uma só célula separados por ponto e vírgula, violando a primeira forma normal.

Nesse formato, perguntas simples ficam caras ou impossíveis: quantos artistas distintos existem, quais participam de mais faixas, qual a música mais popular de cada gênero. O objetivo do projeto foi transformar esse arquivo em um modelo relacional consultável e expor essas consultas em uma interface web.

---

## Arquitetura

O sistema segue uma arquitetura em três camadas, com as três implantadas separadamente na nuvem.

```
  [ Apresentação ]              [ Aplicação ]              [ Dados ]
  +----------------+           +----------------+        +----------------+
  |  React + Vite  |  ------>  |   Flask API    | -----> |  MySQL (Aiven) |
  |    (Render)    |   HTTP    |    (Render)    |  TCP   |                |
  +----------------+  <------  +----------------+ <----- +----------------+
                        JSON                   SQLAlchemy / PyMySQL
```

- **Apresentação:** SPA em React 19 com Vite. Consome a API via `fetch` e trata as respostas em JSON, sem recarregar a página.
- **Aplicação:** API REST em Flask. Usa SQLAlchemy com o driver PyMySQL, com as consultas SQL isoladas das rotas HTTP em um módulo próprio (`queries.py`).
- **Dados:** MySQL gerenciado na Aiven, acessado remotamente pelo servidor de aplicação.

---

## Modelo de dados

Quatro entidades principais e uma tabela associativa:

| Tabela | Registros | Papel |
| --- | --- | --- |
| `MUSICA` | 89.740 | faixa, com popularidade, duração e FKs para álbum e gênero |
| `ARTISTA` | 29.858 | artista isolado a partir do campo composto original |
| `ALBUM` | 46.589 | álbum ao qual a faixa pertence |
| `GENERO` | 113 | gênero atribuído pelo Spotify |
| `PARTICIPACAO` | 123.424 | associativa N:N entre música e artista, com `tipo_participacao` |

A relação entre artista e música é N:N, já que uma faixa pode ter vários artistas e um artista aparece em várias faixas. Essa relação carrega o atributo `tipo_participacao`, que distingue artista principal de participação (`feat`). Os diagramas conceitual, lógico e físico estão em `/model`, e o DDL completo em `/sql/management`.

---

## Pipeline de ETL

O tratamento do dataset é feito por scripts Python em `/scripts`, e o resultado são CSVs atômicos, um por entidade, prontos para carga.

```
114.000 linhas brutas
  → 113.999 após remover nulos
  →  89.740 após remover duplicatas
```

| Script | Papel |
| --- | --- |
| `process_dataset.py` | Análise exploratória: colunas, contagem de nulos, cardinalidade de artistas, álbuns e gêneros. Usado para entender o dataset antes de modelar. |
| `clean_dataset.py` | Isola a etapa de limpeza e reporta o número de linhas em cada estágio, servindo como verificação dos totais. |
| `generate_csv_tables.py` | O pipeline completo: limpa, gera as cinco tabelas, quebra o campo composto de artistas e exporta os CSVs em `/scripts_output`. |

O que o pipeline faz:

1. **Descarta o índice residual** (`Unnamed: 0`) do CSV original.
2. **Remove nulos** nos campos que não podem faltar: `track_id`, `artists`, `album_name` e `track_name`.
3. **Remove duplicatas** por `track_id`.
4. **Deriva as dimensões:** gêneros, álbuns e artistas são deduplicados e recebem IDs sequenciais próprios, já que no CSV se repetem a cada linha.
5. **Quebra a atomicidade:** o campo `artists` é dividido por `;`, cada artista vira uma linha em `PARTICIPACAO`, com o primeiro marcado como `principal` e os demais como `feat`.
6. **Exporta** os cinco CSVs com todos os campos entre aspas, necessário porque nomes de músicas e álbuns contêm vírgulas.

A carga no MySQL respeita a ordem de dependência das chaves estrangeiras: `GENERO` → `ALBUM` → `ARTISTA` → `MUSICA` → `PARTICIPACAO`. Fora dessa ordem, a integridade referencial rejeita as inserções.

---

## Funcionalidades

A aplicação tem quatro telas, todas com busca, ordenação e paginação de 10 registros:

- **Músicas** — lista as faixas com artista, álbum, gênero, duração formatada e popularidade. A busca aceita quatro campos (música, artista, álbum ou gênero) e a ordenação, seis.
- **Artistas** — para cada artista, popularidade média, número de faixas e número de álbuns, com uma visão de detalhe trazendo as cinco músicas mais populares e os três álbuns de maior média.
- **Gêneros** — quantidade de músicas, popularidade média e número de artistas por gênero.
- **Estatísticas** — cinco recortes analíticos: top 10 artistas, top 10 gêneros, artistas com produção acima da média geral da base, música mais popular de cada gênero e álbuns com mais faixas.

As consultas usam funções de agregação (`COUNT`, `AVG`, `MAX`), `GROUP BY` com `HAVING` e subconsultas. As sete consultas ficam em `project/app/queries.py`, e as versões standalone em `/sql/queries`.

---

## Decisões técnicas

**Tabela associativa em vez de campo multivalorado.** Manter os artistas concatenados na tabela de músicas seria mais simples de carregar, mas inviabilizaria qualquer consulta por artista. A tabela `PARTICIPACAO` custou uma etapa a mais no ETL e gerou 123.424 linhas, e é o que permite responder "em quantas faixas este artista aparece" com um `COUNT` em vez de varredura de strings.

**Busca por prefixo em vez de substring.** A barra de busca usa `LIKE 'termo%'`, não `LIKE '%termo%'`. A diferença é de uma porcentagem no código e enorme na execução: com o curinga só à direita o MySQL usa o índice da coluna; com curinga dos dois lados ele é obrigado a varrer as 89.740 linhas a cada tecla digitada. O custo é que a busca não encontra o termo no meio da palavra. Para um catálogo desse tamanho consultado remotamente, a troca compensa.

**SQL parametrizado com whitelist de identificadores.** As consultas são montadas dinamicamente porque a interface permite escolher campo de busca e critério de ordenação. Valores de busca vão como parâmetros vinculados (`:search_value`), nunca concatenados. Já nomes de coluna não podem ser parametrizados por bind, então `queries.py` mantém dicionários (`SEARCH_FIELDS`, `ORDER_TYPES`) que traduzem o identificador recebido do front para o nome real da coluna e rejeitam qualquer valor fora do mapa. A direção da ordenação segue a mesma regra: só `ASC` ou `DESC` chegam à consulta. Isso mantém a flexibilidade da interface sem abrir nenhum ponto da query para entrada arbitrária.

**SQL explícito em vez de ORM puro.** O SQLAlchemy é usado como camada de conexão e mapeamento, mas as consultas analíticas foram escritas diretamente em SQL. Como o objetivo da disciplina era exercitar consultas relacionais, gerar as agregações e subconsultas pelo ORM esconderia justamente o que o projeto precisava demonstrar. As consultas ficam em um módulo separado das rotas, o que mantém o SQL legível e testável isoladamente.

**Paginação no banco, não na aplicação.** Cada rota executa duas consultas: uma com `LIMIT` para a página pedida e outra com `COUNT` para o total. Trazer 89.740 linhas e paginar em memória seria mais simples de escrever e inviável na prática, ainda mais com o banco em outra máquina.

**Três serviços separados em vez de um monolito.** Servir o front pelo próprio Flask seria mais rápido de publicar. Separar em três serviços obrigou a lidar com CORS, variáveis de ambiente por ambiente e latência de rede entre aplicação e banco, que são problemas reais de produção e não apareceriam em uma aplicação local.

**Banco gerenciado em vez de local.** Hospedar o MySQL na Aiven expôs uma questão que o ambiente local esconde: cada consulta paga o custo da rede. Isso tornou visível o peso das consultas com múltiplos `JOIN` sobre a tabela de participações e reforçou as decisões de paginar tudo no banco e manter a busca indexável.

---

## Tecnologias

| Escopo | Ferramentas |
| --- | --- |
| Modelagem | brModelo, MySQL Workbench, DBeaver |
| Banco de dados | MySQL, Aiven (serviço gerenciado) |
| ETL | Python 3, pandas |
| Back-end | Flask, SQLAlchemy, PyMySQL, Flask-CORS, Gunicorn |
| Front-end | React 19, Vite, lucide-react, CSS3 |
| Infraestrutura | Git, GitHub, Render |

---

## Estrutura do projeto

```text
PF-2026.1-BD-Spotify/
│
├── dataset/              # CSV bruto do Kaggle
├── scripts/              # pipeline em Python
│   ├── process_dataset.py        # análise exploratória do dataset
│   ├── clean_dataset.py          # limpeza isolada, com contagem por etapa
│   └── generate_csv_tables.py    # ETL completo: normaliza e exporta os CSVs
├── scripts_output/       # CSVs atômicos gerados pelo ETL
├── model/                # modelos conceitual, lógico e físico (brModelo)
├── sql/
│   ├── management/           # DDL: criação de banco, tabelas e importação
│   └── queries/              # as 7 consultas em arquivos isolados
├── database/             # dump completo do banco populado (.sql)
├── project/
│   ├── app/                  # back-end Flask
│   │   ├── config.py             # conexão e variáveis de ambiente
│   │   ├── models.py             # mapeamento ORM das cinco tabelas
│   │   ├── queries.py            # consultas SQL e whitelists de identificadores
│   │   └── routes.py             # endpoints REST
│   ├── frontend/             # SPA em React + Vite
│   │   └── src/
│   │       ├── tabs/             # as 4 telas
│   │       ├── components/       # tabela, busca, ordenação, paginação
│   │       └── assets/styles/    # CSS por tela
│   ├── frontend_mockup/      # protótipo estático anterior à SPA
│   ├── .env.example
│   └── run.py
├── relatorios/           # relatório técnico do projeto
├── screenshots/          # evidências de banco: DESCRIBE, SELECT e consultas
├── app_screenshots/      # capturas da interface
└── requirements.txt
```

---

## Executando localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/Rebornned/PF-2026.1-BD-Spotify.git
cd PF-2026.1-BD-Spotify
```

### 2. Preparar o back-end

```bash
cd project
python -m venv venv
```

Ative o ambiente virtual:

- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Windows (CMD): `venv\Scripts\activate.bat`
- Linux/macOS: `source venv/bin/activate`

Instale as dependências:

```bash
pip install -r ../requirements.txt
```

### 3. Configurar as variáveis de ambiente

```bash
cp .env.example .env
```

Para um banco local:

```env
DB_USER=root
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306
DB_NAME=spotify_db
SECRET_KEY=sua_chave_secreta
```

Para um banco remoto:

```env
DATABASE_URL=mysql+pymysql://usuario:senha@host:porta/nome_do_banco
SECRET_KEY=sua_chave_secreta
```

Se `DATABASE_URL` estiver preenchida, ela tem prioridade sobre as variáveis individuais. Para ver as consultas SQL no console durante o desenvolvimento, defina `SQLALCHEMY_ECHO=1`.

### 4. Carregar o banco

```sql
CREATE DATABASE spotify_db;
```

```bash
mysql -u seu_usuario -p spotify_db < ../database/spotify_db_export.sql
```

O dump já contém o esquema e os dados tratados, então não é necessário rodar o ETL para usar a aplicação.

Para reproduzir o pipeline do zero, baixe o CSV do Kaggle para `/dataset` e rode o script de dentro da própria pasta, já que os caminhos são relativos a ela:

```bash
cd scripts
python generate_csv_tables.py
```

Os CSVs gerados em `/scripts_output` podem então ser importados com os arquivos de `/sql/management`.

### 5. Subir a API

```bash
python run.py
```

A API responde em `http://127.0.0.1:5000`.

### 6. Subir o front-end

Em outro terminal:

```bash
cd project/frontend
npm install
npm run dev
```

A interface fica em `http://127.0.0.1:5173`.

Por padrão o front aponta para `http://localhost:5000`. Para usar outro endereço, crie um `.env` em `project/frontend/`:

```env
VITE_API_URL=http://endereco-da-api
```

---

## Endpoints

| Método | Rota | Parâmetros |
| --- | --- | --- |
| `GET` | `/api/musicas` | `busca`, `campoBusca`, `ordem`, `direcao`, `pagina` |
| `GET` | `/api/artistas` | `busca`, `pagina` |
| `GET` | `/api/artistas/detalhes` | `nome` |
| `GET` | `/api/generos` | `busca`, `ordem`, `direcao`, `pagina` |
| `GET` | `/api/estatisticas` | `tipo` |

As rotas paginadas devolvem `{ dados, total }`, onde `total` alimenta o controle de paginação no front.

---

## Telas

### Músicas

<p align="center">
  <img src="./app_screenshots/index_musics.png" alt="Tela de músicas" width="100%">
</p>

### Artistas

<p align="center">
  <img src="./app_screenshots/index_artists.png" alt="Tela de artistas" width="100%">
</p>

### Gêneros

<p align="center">
  <img src="./app_screenshots/index_genres.png" alt="Tela de gêneros" width="100%">
</p>

### Estatísticas

<p align="center">
  <img src="./app_screenshots/index_statistics.png" alt="Tela de estatísticas" width="100%">
</p>

---

## Minhas contribuições

Projeto acadêmico desenvolvido em grupo de cinco integrantes. Fui responsável por:

- Modelagem conceitual, lógica e física do banco, e normalização até a 3FN
- Pipeline de ETL em Python: limpeza, derivação das dimensões e quebra da relação N:N
- Escrita das sete consultas SQL e da camada de montagem dinâmica com whitelist
- Arquitetura e desenvolvimento da API em Flask com SQLAlchemy
- Integração entre front-end e back-end
- Deploy das três camadas na nuvem (Render e Aiven)
- Estruturação do repositório e redação da documentação técnica

O histórico de commits deste repositório registra o desenvolvimento.

---

## Créditos

Dataset: [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshifichadia/spotify-tracks-dataset), via Kaggle.

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](./LICENSE) para mais detalhes.
