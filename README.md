# 📊 Painel Gerencial de Atendimento - SZ Chat (TRE-PB)

Dashboard interativo desenvolvido em **Streamlit** para acompanhamento gerencial, análise sintética e auditoria dos atendimentos prestados via SZ Chat no Tribunal Regional Eleitoral da Paraíba (TRE-PB).

---

## 🎯 Objetivo

Visualizar os resultados consolidados do processamento semântico das conversas, garantindo conformidade com a **Lei Geral de Proteção de Dados (LGPD)** e oferecendo métricas operacionais para a gestão do SZ Chat.

---

## 🚀 Funcionalidades do Dashboard

- **KPIs Operacionais:** Volume total de chamados, taxa de resolução efetiva, duração média de atendimento (TMA), uso de mensagens de áudio, chamadas sem resposta humana e tempo de ociosidade de encerramento.
- **Análise por Turno Eleitoral:** Filtro dedicado para navegação entre atendimentos do **1º Turno** e do **2º Turno** das eleições.
- **Análise Semântica:** Distribuição dos atendimentos por assunto principal, avaliação de qualidade/cordialidade do operador e status da solução.
- **Análise Temporal:** Gráfico de horários de pico para identificação das faixas horárias com maior demanda.
- **Filtros Interativos:** Seleção por turno, período (data), atendente responsável, assunto principal e status de resolução.
- **Relatório Executivo Oficial:** Emissão e download de relatório em HTML/PDF formatado com introdução institucional do Serviço de Atendimento ao Eleitor (SAE / CRE) e tabelas consolidadas.
- **Consulta ao Histórico Anonimizado:** Tabela detalhada dos protocolos incluindo o diálogo completo mascarado (preservando a privacidade dos eleitores) e exportação da base consolidada.

---

## 🛡️ Conformidade com a LGPD (Anonimização)

Os dados exibidos na aplicação passaram por regras estritas de anonimização (PII) antes da geração do relatório final:

- **CPFs:** Mapeados e substituídos no formato `123.***.***-**`.
- **Títulos de Eleitor:** Substituídos por `**** **** 9012`.
- **Telefones:** Mascarados no padrão `(83) 9****-**77`.
- **Nomes Próprios:** Mascarados preservando a 1ª letra e o sobrenome principal (ex: `J***************Silva`).

---

## 📁 Estrutura do Repositório

```text
.
├── .github/
│   └── workflows/
│       └── keep_alive.yml       # Automacão GitHub Actions para evitar o modo 'sleep' do Streamlit Cloud
├── app.py                      # Aplicação principal do Dashboard Streamlit
├── gerar_relatorio.py          # Módulo de compilação do Relatório Executivo em HTML
├── atendimentos_analisados.csv # Base consolidada e anonimizada de atendimentos
├── requirements.txt            # Dependências da aplicação Python
├── .gitignore                  # Arquivos ignorados pelo Git (dados brutos e scripts internos)
└── README.md                   # Documentação do projeto
```

## ⚙️ Manutenção de Disponibilidade (Keep-Alive Automático)

Para evitar que a aplicação entre em modo de hibernação (_sleep mode_) no Streamlit Community Cloud devido ao intervalo entre acessos, o repositório conta com um fluxo automatizado do **GitHub Actions** (`keep_alive.yml`).

- **Frequência:** Realiza uma requisição HTTP automática a cada 6 horas (`0 */6 * * *`).
- **Objetivo:** Manter a aplicação permanentemente "acordada" e pronta para acesso imediato pelos usuários da intranet/gestão.

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

```bash
pip install -r requirements.txt
```

### 4. Executar o aplicativo Streamlit

```bash
streamlit run app.py
```

Acesse o painel no navegador através do endereço: `http://localhost:8501`.

---

## 💻 Tecnologias Utilizadas

- **Python 3.10+**
- **Streamlit:** Interface gráfica interativa.
- **Pandas:** Manipulação, filtragem e cruzamento de dados.
- **Plotly Express:** Visualização gráfica dinâmica.
- **GitHub Actions:** Automação de rotina de disponibilidade (_keep-alive_).

---

## 🔒 Proteção de Dados e Conformidade (LGPD)

Em atendimento à **Lei Geral de Proteção de Dados (Lei nº 13.709/2018)**:

- Todo o processamento de inteligência artificial/análise sintética é realizado de forma **100% offline e local**, sem envio de dados para APIs de terceiros na nuvem.
- Os dados sensíveis contidos no histórico das conversas passam por regras de mascaramento prévio antes do deploy da base consolidada:
  - **CPF:** `123.***.***-**`
  - **Título de Eleitor:** `**** **** 9012`
  - **Telefone:** `(83) 9****-**77`
  - **Nomes Próprios:** `J***************Silva`

---

_Desenvolvido para auditoria interna, acompanhamento de qualidade e conformidade com a LGPD no Serviço de Atendimento ao Eleitor (SAE) da Corregedoria Regional Eleitoral (TRE-PB)._
