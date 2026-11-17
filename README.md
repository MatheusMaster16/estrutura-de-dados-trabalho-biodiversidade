**Quem observa a biodiversidade brasileira?** 
Projeto de Ciência de Dados: registros de animais no Brasil (API do GBIF) cruzados com população e área (API do IBGE).

**Matheus Felipe de Oliveira**

**1. Tema e justificativa**

. Dificuldade com a manipulação da API do tema escolhido anteriormente, onde a chave da API era ligada a conta individual do Steam, me levou a buscar API's totalmente gratuitas;

. O pivotamento para animais se deu a vivencias recentes com observações de um Beija-Flor que fez um ninho no meu quintal;

. O Brasil tem a maior biodiversidade do planeta, mas o que se sabe sobre ela depende de **quem registra os animais e onde**. Hoje, a maior parte dos registros vem de pessoas comuns, como nós, usando aplicativos no celular, e não só de pesquisadores e museus;

. O tema central (Quem observa a biodiversidade brasileira?) visa descobrir se o país é registrado por igual ou se existem lugares "esquecidos" nos dados. Isso importa porque decisões de conservação usam esses registros;

. Trouxe a análise para Jundiaí para ver como isso aparece na nossa própria região.

**2. Fonte dos dados (APIs)**

| API | Endereço | Dados usados |

| **GBIF** (Global Biodiversity Information Facility) | 'https://api.gbif.org/v1/occurrence/search' | Registros de animais no Brasil de 2000 a 2025, contados por ano, estado, tipo de registro, grupo de animais, mês e categoria de ameaça. Os mesmos dados para Jundiaí e 6 cidades vizinhas, e os beija-flores de Jundiaí. |

| **GBIF** (espécies e conjuntos de dados) | 'https://api.gbif.org/v1/species/...' e 'https://api.gbif.org/v1/dataset/...' | Nome científico e classe das espécies e nome das instituições que publicaram os dados. |

| **IBGE** (API de Agregados) | 'https://servicodados.ibge.gov.br/api/v3/agregados/4714/...' | População e área (km²) dos estados e das cidades, Censo 2022. |

**Sobre os dados:** cada registro do GBIF é um animal observado ou coletado em um lugar e uma data. Como são mais de 24 milhões de registros no Brasil, usamos o recurso de **facet** da API: em vez de baixar todos os registros, a API devolve as contagens já agrupadas (por exemplo, quantos registros por estado). Nenhuma das APIs precisa de chave ou senha.

Os dados das APIs são salvos sem alteração em 'dados_brutos/' (arquivos '.json'). Depois de limpos e organizados, ficam em 'dados_tratados/' (arquivos '.csv'), que é de onde o dashboard lê.
