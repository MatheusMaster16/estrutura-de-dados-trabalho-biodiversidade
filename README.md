**Quem observa a biodiversidade brasileira?** 
Projeto de Ciência de Dados: registros de animais no Brasil (API do GBIF) cruzados com população e área (API do IBGE).

**Matheus Felipe de Oliveira**

**1. Tema e justificativa**

- A dificuldade com a manipulação da API do tema escolhido anteriormente, onde a chave da API era ligada a conta individual do Steam, me levou a buscar API's totalmente gratuitas;
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

1. pip install -r requirements.txt     (# 1. instala as bibliotecas)
2. python 1_coleta.py                 (# 2. busca os dados nas APIs)
3. python 2_tratamento.py              (# 3. limpa e organiza os dados)
4. python -m streamlit run 3_dash.py   (# 4. abre o dashboard no navegador)

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
<img width="306" height="523" alt="image" src="https://github.com/user-attachments/assets/2b2dce45-0e0f-4fb1-b780-cbb9d2e7326a" />

**Indicadores (KPIs):** total de registros no período, estado líder, % de observação humana e % de registros com estado reconhecido. Na aba de Jundiaí: registros, registros por km², % de insetos e % de espécimes de museu.

**Evolução**
<img width="1920" height="904" alt="image" src="https://github.com/user-attachments/assets/277cab20-ccf2-4f64-a1f7-64043197d77e" />
Mostra quantos registros foram feitos por ano e de que tipo. Os registros por ano passaram de **112.690 (2000) para 4.323.776 (2025)**, cerca de 38 vezes mais. A observação feita por pessoas foi de **30,3% para 99,8%** dos registros, e os espécimes de museu caíram de 62,5% para 0,1%.

**Estados**
<img width="1544" height="830" alt="image" src="https://github.com/user-attachments/assets/0e0875ea-3309-4b76-9d97-3b9cd8694f98" />
Compara os estados e as regiões na medida escolhida no botão de rádio. **SP, MG e RJ somam 45,2%** dos registros. Por km², o **Sudeste tem 12,63 registros e o Norte 0,68**, 18,5 vezes menos. A correlação entre população e registros é **0,74**. O dashboard aponta **7 pontos cegos**, estados abaixo da mediana tanto por km² quanto por habitante: Piauí, Maranhão, Amapá, Pará, Bahia, Sergipe e Goiás.

**Grupos de animais**
<img width="1509" height="816" alt="image" src="https://github.com/user-attachments/assets/19a6feb3-1c6f-433c-bddb-72ae311828c9" />
<img width="1881" height="650" alt="image" src="https://github.com/user-attachments/assets/2cf00510-0248-4bb4-9091-c959737f17c1" />
Mostra quais grupos de animais são mais registrados e em que meses. As **aves são 90%** dos registros. O gráfico de meses muda com o grupo escolhido: anfíbios têm pico em **janeiro** (14,0% do ano) e mínimo em junho (4,4%); aves têm pico em **outubro** (12,8%).

**Espécies ameaçadas**
<img width="1545" height="566" alt="image" src="https://github.com/user-attachments/assets/f95468e5-e0a1-47d5-aeef-5c2fda381106" />
Mostra onde estão os registros de espécies ameaçadas e quais espécies aparecem. O **Mato Grosso** tem a maior parte desses registros (19,7%). O **peixe-boi** sozinho tem 121.861 registros, **41,8%** de todos os registros de espécies vulneráveis.

**Jundiaí em foco**
<img width="1521" height="713" alt="image" src="https://github.com/user-attachments/assets/d1e5e133-f906-4c27-ae2f-ab5be9f1d20d" />
<img width="1517" height="575" alt="image" src="https://github.com/user-attachments/assets/6ea4a1a8-9fa3-4fa1-89c4-87a5ec3c42f1" />
Compara Jundiaí com o Brasil e com as cidades vizinhas. A cidade tem **79.004 registros**, e **24,5% são insetos** (no Brasil, 6,1%): 13.143 dos 19.341 registros de insetos citam a **Reserva Biológica da Serra do Japi**. A vizinha **Várzea Paulista**, com 115.771 habitantes, tem só **104 registros**. Entre as espécies ameaçadas da cidade aparece um hamster-dourado com um único registro, quase certamente um animal de estimação. No fim da aba, **2.074 registros de beija-flores, de 20 espécies**; o mais comum é o beija-flor-tesoura (21,8%).

**Qualidade dos dados**
<img width="1501" height="689" alt="image" src="https://github.com/user-attachments/assets/f9ad2aa4-f3c9-4b1b-a60b-1143f85f3f57" />
Mostra o resultado da limpeza: de 653 grafias de estado para 27 estados. **3,9%** dos registros não informam o estado; eles entram no total do Brasil, mas não nos gráficos por estado.

**6. Principais conclusões**
1. **Quem registra a fauna mudou:** em 2025, 99,8% dos registros são observações de pessoas, feitas com aplicativos de ciência popular.
2. **Os dados mostram onde há gente, não onde há bicho:** o Norte, onde está a Amazônia, tem 18 vezes menos registros por km² que o Sudeste.
3. **As aves dominam:** são 90% dos registros, enquanto os insetos, o grupo mais diverso do planeta, são 6%.
4. **O registro tem estação:** anfíbios são mais registrados no verão chuvoso; aves, em outubro.
5. **Poucas espécies concentram os registros de ameaça:** só o peixe-boi tem 41,8% dos registros de espécies vulneráveis.
6. **Jundiaí é diferente por causa da Serra do Japi:** a cidade tem quatro vezes mais insetos, na proporção, que o Brasil.
7. **Existe um ponto cego ao lado da faculdade:** Várzea Paulista tem 0,9 registro por 1.000 habitantes, contra 178,2 em Jundiaí.

**7. Limitações**

- Mais registros **não** significam mais animais, e sim mais pessoas observando.
- Peixes não entraram: o GBIF não tem uma classe única para os peixes ósseos.
- A categoria de ameaça é a da IUCN (lista mundial), que pode ser diferente da lista oficial do Brasil.
- Os nomes populares das espécies foram adicionados à mão.

Dados do [GBIF.org](https://www.gbif.org) e do [IBGE](https://www.ibge.gov.br). Categorias de ameaça: [IUCN](https://www.iucnredlist.org).

<img width="512" height="398" alt="beija-flor" src="https://github.com/user-attachments/assets/18ac16d0-226b-4550-a862-e263a58fa127" />






















