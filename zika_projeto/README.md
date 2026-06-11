# Projeto: Banco de Dados Epidemiológico — Zika SINAN 2018–2026

## Estrutura do projeto

```
zika_projeto/
├── .env                            ← credenciais do banco (edite antes de tudo)
├── setup.py                        ← roda a Etapa 1 completa
├── setup.log                       ← gerado ao rodar o setup.py
├── data/
│   └── ZIKA_BR_2018_2026_UNIFICADO.csv   ← coloque o CSV aqui
├── etapa1/
│   ├── schema.sql                  ← cria todas as tabelas
│   └── indices.sql                 ← cria os índices pós-carga
├── etapa2_funcoes_triggers/        ← Colega B
├── etapa3_views/                   ← Colega B
└── etapa4_analise/                 ← Colega C
```

---

## Pré-requisitos

- **PostgreSQL 15+** com **pgAdmin** (baixe em https://www.postgresql.org/download/)
- **Python 3.10+** (baixe em https://www.python.org/)

---

## Passo a passo (todos os colegas fazem isso)

### 1. Instale as dependências Python

Abra o terminal (Prompt de Comando ou PowerShell no Windows) e rode:

```
pip install psycopg2-binary pandas python-dotenv tqdm
```

### 2. Crie o banco no pgAdmin

1. Abra o pgAdmin
2. Clique com o botão direito em **Databases → Create → Database**
3. Nome: `zika_db` (ou o nome que preferir)
4. Clique em **Save**

### 3. Edite o arquivo `.env`

Abra o `.env` na raiz do projeto e preencha com suas credenciais:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zika_db
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
```

A senha é a que você definiu ao instalar o PostgreSQL.

### 4. Coloque o CSV na pasta `data/`

O arquivo deve se chamar exatamente:
```
data/ZIKA_BR_2018_2026_UNIFICADO.csv
```

### 5. Rode o setup

No terminal, na raiz do projeto:

```
python setup.py
```

A carga de 236 mil registros leva cerca de 2–5 minutos.
Ao final, o terminal mostra um resumo. O log completo fica em `setup.log`.

### 6. Verifique no pgAdmin

Abra o pgAdmin, conecte ao `zika_db` e rode no Query Tool:

```sql
SELECT classi_fin, COUNT(*) FROM notificacao GROUP BY 1 ORDER BY 1;
```

A linha com `classi_fin = 1` mostra os casos confirmados carregados.

---

## Parâmetros de conexão (para os scripts das outras etapas)

| Parâmetro | Valor padrão |
|-----------|-------------|
| Host      | localhost   |
| Porta     | 5432        |
| Banco     | zika_db     |
| Usuário   | postgres    |

Os colegas B e C devem usar as mesmas credenciais do `.env`
para conectar nos scripts das Etapas 2, 3 e 4.

---

## Dicionário rápido das colunas mais usadas

| Coluna        | Significado                                                  |
|---------------|--------------------------------------------------------------|
| `classi_fin`  | **1 = Confirmado** — sempre filtre por isso nas análises     |
| `dt_sin_pri`  | Data dos primeiros sintomas — base para a curva epidêmica    |
| `sem_pri`     | Semana epidemiológica dos sintomas (1–53)                    |
| `sg_uf_not`   | UF de notificação (código IBGE 2 dígitos)                    |
| `sg_uf`       | UF de residência do paciente                                 |
| `nu_idade_n`  | Idade codificada — precisa de `decode_idade()` (Etapa 2)     |
| `cs_gestant`  | Gestação: 1–3 = trimestres, 5 = não gestante, 6 = n/a        |
| `cs_sexo`     | M / F / I                                                    |
| `evolucao`    | 1 = Cura, 2 = Óbito pelo agravo                              |

Consulte `Catálogo_de_Variáveis` para a descrição completa.
