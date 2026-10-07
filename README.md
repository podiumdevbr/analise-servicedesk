# 📊 Painel Gerencial de Atendimento - SZ Chat (TRE-PB)

Dashboard interativo desenvolvido em **Streamlit** para acompanhamento gerencial, análise sintética e auditoria dos atendimentos prestados via SZ Chat no Tribunal Regional Eleitoral da Paraíba (TRE-PB).

---

## 🎯 Objetivo

Visualizar os resultados consolidados do processamento semântico das conversas, garantindo conformidade com a **Lei Geral de Proteção de Dados (LGPD)** e oferecendo métricas operacionais para a gestão do SZ Chat.

---

## 🚀 Funcionalidades do Dashboard

- **KPIs Operacionais:** Volume total de chamados, taxa de resolução, atendimentos com mensagens de áudio e solicitações sem resposta humana.
- **Análise Semântica:** Distribuição dos atendimentos por assunto principal, avaliação de qualidade/cordialidade do operador e status da solução.
- **Análise Temporal:** Gráfico de horários de pico para identificação das faixas horárias com maior demanda.
- **Filtros Interativos:** Seleção por período (data), atendente responsável, assunto principal e status de resolução.
- **Consulta ao Histórico Anonimizado:** Tabela detalhada dos protocolos incluindo o diálogo completo mascarado (preservando a privacidade dos eleitores) e exportação da base consolidada.

---

## 🛡️ Conformidade com a LGPD (Anonimização)

Os dados exibidos na aplicação passaram por regras estritas de anonimização (PII) antes da geração do relatório final:

- **CPFs:** Mapeados e substituídos no formato `123.***.***-**`.
- **Títulos de Eleitor:** Substituídos por `**** **** 9012`.
- **Telefones:** Mascarados no padrão `(83) 9****-7777`.
- **Nomes Próprios:** Mascarados preservando a 1ª letra e o sobrenome principal (ex: `J***************Silva`).

---

## 📁 Estrutura do Repositório

```text
.
├── app.py                      # Aplicação principal do Dashboard Streamlit
├── atendimentos_analisados.csv # Base consolidada e anonimizada de atendimentos
├── requirements.txt            # Dependências da aplicação Python
├── .gitignore                  # Arquivos ignorados pelo Git (dados brutos e scripts internos)
└── README.md                   # Documentação do projeto
```

---

## 💻 Como Executar o Dashboard Localmente

### 1. Clonar o repositório

```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
```

### 2. Criar e ativar um ambiente virtual (recomendado)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

````bash
pip install -r requirements.txt

### 4. Executar o aplicativo Streamlit
```bash
streamlit run app.py
````

Acesse o painel no navegador através do endereço: `http://localhost:8501`.

---

## 💻 Tecnologias Utilizadas

- Python 3.10+
- Streamlit: Interface gráfica interativa.
- Pandas: Manipulação e filtragem dos dados.
- Plotly Express: Visualização de gráficos dinâmicos.

---

## 🔒 Proteção de Dados e Conformidade (LGPD)

Em atendimento à **Lei Geral de Proteção de Dados (Lei nº 13.709/2018)**:

- Todo o processamento de IA é realizado de forma **100% offline e local**, sem envio de dados para APIs de terceiros na nuvem.
- Os dados sensíveis contidos no histórico das conversas passam por regras de mascaramento antes da geração da base final:
  - **CPF:** `123.***.***-**`
  - **Título de Eleitor:** `**** **** 9012`
  - **Telefone:** `(83) 9****-**77`
  - **Nomes Próprios:** `J***************Silva`

---

_Desenvolvido para auditoria interna, acompanhamento de qualidade e conformidade com a LGPD no SZ Chat do TRE-PB._
