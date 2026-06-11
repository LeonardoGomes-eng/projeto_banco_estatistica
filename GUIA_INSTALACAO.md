# 🚀 Guia de Instalação e Setup - Análise Estatística Avançada

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL com banco de dados `zika_db` já populado
- pip ou conda para gerenciamento de pacotes

## 📦 Instalação das Dependências

### Opção 1: Instalação Rápida (Recomendado)

```bash
cd dashboard
pip install -r requirements.txt
```

### Opção 2: Instalação Manual

```bash
# Pacotes base (já podem estar instalados)
pip install streamlit>=1.36.0
pip install pandas>=2.0.0
pip install plotly>=5.18.0

# Novos pacotes para análise estatística
pip install prophet>=1.1.5
pip install scikit-learn>=1.3.0
pip install scipy>=1.10.0
pip install statsmodels>=0.14.0
pip install numpy>=1.24.0
```

### Opção 3: Instalação com Conda

```bash
conda create -n zika-analysis python=3.10
conda activate zika-analysis
conda install -c conda-forge prophet
pip install streamlit pandas plotly psycopg2-binary python-dotenv sqlalchemy scikit-learn scipy statsmodels
```

## ⚙️ Configuração

### 1. Arquivo `.env`

Certifique-se que você tem as variáveis de ambiente corretas:

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=zika_db
DB_USER=postgres
DB_PASSWORD=sua_senha
```

### 2. Verifique a Conexão com o Banco

```python
from config.database import fetch_data

# Teste a conexão
df = fetch_data("SELECT COUNT(*) as total FROM notificacoes;")
print(df)
```

## 🚀 Executar o Dashboard

```bash
cd dashboard
streamlit run app.py
```

O dashboard abrirá em `http://localhost:8501`

## ✅ Verificar Instalação

### Verificar se todas as dependências estão instaladas

```bash
# No terminal
python -c "import prophet; print('Prophet OK')"
python -c "import sklearn; print('Scikit-learn OK')"
python -c "import statsmodels; print('Statsmodels OK')"
python -c "import streamlit; print('Streamlit OK')"
```

### Executar exemplos de teste

```bash
cd dashboard
python examples_statistical_analysis.py
```

Você deve ver output como:
```
╔════════════════════════════════════════════════════════════╗
║     EXEMPLOS DE USO - ANÁLISE ESTATÍSTICA AVANÇADA         ║
╚════════════════════════════════════════════════════════════╝

============================================================
EXEMPLO 1: ANÁLISE DE SAZONALIDADE
============================================================
✓ Sazonalidade analisada com sucesso
  - Período: 52 semanas
  - Amplitude Sazonal: XX.XX casos
  ...
```

## 🔧 Solução de Problemas

### Prophet não instala

**Erro comum:**
```
ERROR: Could not build wheels for prophet, which is required to install pyproject.toml-based projects
```

**Solução:**
```bash
pip install --no-build-isolation --upgrade prophet
# ou
pip install cmdstanpy==1.1.2 pystan==2.19.1.1
pip install prophet
```

### Erro ao conectar no PostgreSQL

```
psycopg2.OperationalError: could not connect to server
```

**Verificar:**
1. PostgreSQL está rodando
2. Credenciais em `.env` estão corretas
3. Banco de dados `zika_db` existe

```bash
# Testar conexão
psql -h 127.0.0.1 -U postgres -d zika_db -c "SELECT 1;"
```

### Erro ao carregar dados

```
ProgrammingError: relation "notificacoes" does not exist
```

**Verificar:**
- Se a tabela `notificacoes` foi criada
- Se os dados foram carregados no banco

```sql
-- No PostgreSQL
SELECT COUNT(*) FROM notificacoes;
```

### Streamlit abre mas página em branco

1. Verifique o console por erros
2. Confirme se dados estão no banco
3. Tente limpar cache: `streamlit cache clear`

## 📊 Estrutura Esperada

Após instalação correta, sua estrutura deve ser:

```
dashboard/
├── app.py                           # Arquivo principal
├── requirements.txt                 # Dependências
├── examples_statistical_analysis.py # Exemplos
├── config/
│   ├── database.py                 # Conexão BD
│   └── theme.py                    # Tema
├── components/
│   ├── statistical_analysis.py     # ⭐ NOVO: Análises
│   ├── statistical_utils.py        # ⭐ NOVO: Utilitários
│   ├── charts.py
│   ├── filters.py
│   └── kpi_cards.py
├── pages/
│   ├── 01_Visao_Executiva.py
│   ├── 02_Distribuicao_Geografica.py
│   ├── 03_Perfil_Demografico.py
│   ├── 04_Gestantes.py
│   ├── 05_Qualidade_Auditoria.py
│   ├── 06_Monitoramento_Vigilancia.py
│   └── 07_Analise_Estatistica.py   # ⭐ NOVA PÁGINA
└── queries/
    └── dashboard_queries.py
```

## 🎯 Próximos Passos

1. ✅ Instale as dependências
2. ✅ Configure o `.env`
3. ✅ Execute `streamlit run app.py`
4. ✅ Navegue até "Análise Estatística Avançada"
5. ✅ Explore as 4 análises disponíveis

## 📚 Documentação

Para mais detalhes sobre cada análise, veja:
- [ANALISE_ESTATISTICA_DOCS.md](./ANALISE_ESTATISTICA_DOCS.md)

## 💡 Dicas de Performance

- **Primeira execução**: Prophet é lento na primeira previsão (~10s)
- **Cache**: Dados são cache por 1 hora automaticamente
- **Clusters**: Reduzir número de municípios para análises mais rápidas
- **Forecast**: Reduzir número de meses se for muito lento

## 🔐 Segurança

⚠️ **Nunca compartilhe seu `.env` com credenciais!**

Adicione ao `.gitignore`:
```
.env
*.pyc
__pycache__/
.streamlit/
.cache/
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique se Python >= 3.8: `python --version`
2. Verifique dependências: `pip list`
3. Teste exemplos: `python examples_statistical_analysis.py`
4. Verifique banco de dados: `SELECT COUNT(*) FROM notificacoes;`

---

**Versão**: 1.0  
**Data**: Junho 2024  
**Status**: ✅ Pronto para produção
