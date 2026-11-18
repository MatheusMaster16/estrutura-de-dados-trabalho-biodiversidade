**Quem observa a biodiversidade brasileira?** 
Projeto de Ciência de Dados: registros de animais no Brasil (API do GBIF) cruzados com população e área (API do IBGE).

**Matheus Felipe de Oliveira**

**1. Tema e justificativa**

- Dificuldade com a manipulação da API do tema escolhido anteriormente, onde a chave da API era ligada a conta individual do Steam, me levou a buscar API's totalmente gratuitas;
- O pivotamento para animais se deu a vivencias recentes com observações de um Beija-Flor que fez um ninho no meu quintal;
- O Brasil tem a maior biodiversidade do planeta, mas o que se sabe sobre ela depende de **quem registra os animais e onde**. Hoje, a maior parte dos registros vem de pessoas comuns, como nós, usando aplicativos no celular, e não só de pesquisadores e museus;
- O tema central (Quem observa a biodiversidade brasileira?) visa descobrir se o país é registrado por igual ou se existem lugares "esquecidos" nos dados. Isso importa porque decisões de conservação usam esses registros;
- Trouxe a análise para Jundiaí para ver como isso aparece na nossa própria região.

**2. Fonte dos dados (APIs)**

| API | Endereço | Dados usados |

| **GBIF** (Global Biodiversity Information Facility) | [api.gbif.org/v1/occurrence/search](https://api.gbif.org/v1/occurrence/search?country=BR&taxonKey=1&occurrenceStatus=PRESENT&limit=0&facet=stateProvince) | Registros de animais no Brasil de 2000 a 2025, contados por ano, estado, tipo de registro, grupo de animais, mês e categoria de ameaça. Os mesmos dados para Jundiaí e 6 cidades vizinhas, e os beija-flores de Jundiaí. |

| **GBIF** (espécies e conjuntos de dados) | [api.gbif.org/v1/species](https://api.gbif.org/v1/species/2482755) e [api.gbif.org/v1/dataset](https://api.gbif.org/v1/dataset/4fa7b334-ce0d-4e88-aaae-2e0c138d049e) | Nome científico e classe das espécies e nome das instituições que publicaram os dados. |

| **IBGE** (API de Agregados) | [servicodados.ibge.gov.br/api/v3/agregados/4714](https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93%7C6318?localidades=N3%5Ball%5D) | População e área (km²) dos estados e das cidades, Censo 2022. |

**Sobre os dados:** cada registro do GBIF é um animal observado ou coletado em um lugar e uma data. Como são mais de 24 milhões de registros no Brasil, usamos o recurso de **facet** da API: em vez de baixar todos os registros, a API devolve as contagens já agrupadas (por exemplo, quantos registros por estado). Nenhuma das APIs precisa de chave ou senha. 

Os dados das APIs são salvos sem alteração em `dados_brutos/` (arquivos `.json`). Depois de limpos e organizados, ficam em `dados_tratados/` (arquivos `.csv`), que é de onde o dashboard lê.

**3. Perguntas que o dashboard responde**

- Como cresceu o número de registros de animais e **quem** os produz;
- Os estados e as regiões são registrados por igual? Isso tem relação com a **população**? Quais são os **pontos cegos**?;
- Quais **grupos de animais** são mais registrados e **em que meses**?;
- Onde estão os registros de **espécies ameaçadas** de extinção e **quais espécies** aparecem?;
- Como **Jundiaí** se compara com o Brasil e com as cidades vizinhas? Quais **beija-flores** vivem na cidade?;
- Qual é a **qualidade** dos dados e o que precisou ser limpo?.

**4. Como rodar o projeto**

Precisa de **Python** e de **internet**. Abra a pasta no VS Code e rode nesta ordem:

pip install -r requirements.txt     (# 1. instala as bibliotecas)

python 1_coleta.py                 (# 2. busca os dados nas APIs)

python 2_tratamento.py              (# 3. limpa e organiza os dados)

python -m streamlit run 3_dash.py   (# 4. abre o dashboard no navegador)

- O passo 2 cria a pasta `dados_brutos/` e o passo 3 cria a pasta `dados_tratados/`.
- As duas pastas já vêm no repositório. Para só abrir o dashboard, basta fazer os passos 1 e 4.
- O dashboard abre em `http://localhost:8501`.

> O dashboard abre com `python -m streamlit run 3_dash.py`. Rodar `python 3_dash.py` não abre a página.


| Arquivo | O que faz |

| `1_coleta.py` | Pede os dados ao GBIF e ao IBGE com a biblioteca `requests` e salva as respostas em `dados_brutos/` |  

| `2_tratamento.py` | Com `pandas`: padroniza os nomes dos estados, junta com população e área (`merge`), agrupa e soma (`groupby`) e cria colunas novas (registros por km², por 1.000 habitantes, % do ano). Salva em `dados_tratados/` |

| `3_dash.py` | Com `streamlit` e `plotly`: lê as tabelas e mostra os filtros, indicadores e gráficos |

| `requirements.txt` | Bibliotecas usadas |

**Limpeza dos dados:** no GBIF, o nome do estado é texto livre, e cada instituição escreve de um jeito. Encontrei **653 grafias diferentes** ("São Paulo", "Sao Paulo", "SP", "Estado da Bahia"...). Tirei acentos, maiúsculas e prefixos e usei um dicionário para chegar à sigla do estado. Resultado: **27 estados** e **99,9% dos registros reconhecidos**.

**5. O dashboard**

**Filtros (barra lateral):**
- **Slider:** período (de 2000 a 2025);
- **Dropdown:** região do Brasil;
- **Botão de rádio:** forma de medir os estados (total, por km² ou por 1.000 habitantes);
- **Dropdown:** grupo de animais;
- **Caixa de seleção:** mostrar as tabelas de dados.

**Indicadores (KPIs):** total de registros no período, estado líder, % de observação humana e % de registros com estado reconhecido. Na aba de Jundiaí: registros, registros por km², % de insetos e % de espécimes de museu.

<img width="306" height="523" alt="image" src="https://github.com/user-attachments/assets/2b2dce45-0e0f-4fb1-b780-cbb9d2e7326a" />

















