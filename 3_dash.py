#Dash

import json
import os
from urllib.parse import quote

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

PASTA_ETAPA = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADA = os.path.join(PASTA_ETAPA, "dados_tratados")
BEIJA_FLOR = os.path.join(PASTA_ETAPA, "imagens", "beija-flor.png")

st.set_page_config(page_title="Biodiversidade no Brasil", page_icon=BEIJA_FLOR, layout="wide")

@st.cache_data  #guarda o resultado na memória
def carregar_dados():
    dados = {}
    for nome in ["registros_estado_ano", "total_por_ano", "tipo_registro_ano", "grupos_estado",
                 "ameacadas_estado", "jundiai_ano", "jundiai_tipo", "jundiai_grupos",
                 "jundiai_especies", "jundiai_fontes", "cidades_regiao",
                 "sazonalidade_grupo_mes", "especies_ameacadas", "beija_flores_jundiai"]:
        dados[nome] = pd.read_csv(os.path.join(PASTA_ENTRADA, nome + ".csv"))
    with open(os.path.join(PASTA_ENTRADA, "relatorio_limpeza.json"), encoding="utf-8") as arquivo:
        dados["relatorio"] = json.load(arquivo)
    return dados

dados = carregar_dados()
estado_ano = dados["registros_estado_ano"]
total_ano = dados["total_por_ano"]
tipos = dados["tipo_registro_ano"]
grupos = dados["grupos_estado"]
ameacadas = dados["ameacadas_estado"]
relatorio = dados["relatorio"]

def numero_br(valor, casas=0):
    #formata número no padrão brasileiro
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

def link_google(texto):
    #transforma o nome em link de pesquisa no google
    if not texto:
        return ""
    return "https://www.google.com/search?q=" + quote(texto)

def coluna_link(titulo):
    #coluna clicável que mostra só o nome (o trecho depois de "q=")
    return st.column_config.LinkColumn(titulo, display_text=r"q=(.*)", alignment="left")

#titulo
col_logo, col_titulo = st.columns([1, 11], vertical_alignment="center")
col_logo.image(BEIJA_FLOR, width=90)
col_titulo.title("Quem observa a biodiversidade brasileira?")
st.write(
    "Registros de **animais no Brasil** publicados no **GBIF** (base mundial de biodiversidade), "
    "cruzados com **população e área** dos estados (**IBGE**, Censo 2022). "
    "A ideia é entender **onde** e **por quem** a fauna é registrada, e se esse registro é igual em todo o país."
)
#filtros (barra da esquerda)
st.sidebar.header("Filtros")
ano_min, ano_max = int(estado_ano["ano"].min()), int(estado_ano["ano"].max())
periodo = st.sidebar.slider("Período", ano_min, ano_max, (ano_min, ano_max))
regiao = st.sidebar.selectbox("Região", ["Brasil todo", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"])
metrica = st.sidebar.radio(
    "Medir registros por estado como:",
    ["Total de registros", "Registros por km²", "Registros por 1.000 habitantes"],
)
lista_grupos = sorted(grupos["grupo"].unique())
grupo = st.sidebar.selectbox("Grupo de animais", lista_grupos, index=lista_grupos.index("Aves"))
mostrar_tabelas = st.sidebar.checkbox("Mostrar tabelas de dados")
st.sidebar.caption("Fontes: GBIF (api.gbif.org) e IBGE (servicodados.ibge.gov.br)")

#filtros aplicados
filtrado = estado_ano[(estado_ano["ano"] >= periodo[0]) & (estado_ano["ano"] <= periodo[1])]
if regiao != "Brasil todo":
    filtrado = filtrado[filtrado["regiao"] == regiao]
por_estado = filtrado.groupby(["uf", "nome", "regiao", "area_km2", "populacao"], as_index=False)["registros"].sum()
por_estado["Registros por km²"] = por_estado["registros"] / por_estado["area_km2"]
por_estado["Registros por 1.000 habitantes"] = por_estado["registros"] / por_estado["populacao"] * 1000
por_estado["Total de registros"] = por_estado["registros"]
por_estado = por_estado.sort_values(metrica, ascending=False)

#kpi's
total = por_estado["registros"].sum()
lider = por_estado.iloc[0]
tipos_ultimo_ano = tipos[tipos["ano"] == periodo[1]]
pct_humana = tipos_ultimo_ano.loc[tipos_ultimo_ano["tipo"] == "Observação humana", "pct_do_ano"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros no período", numero_br(total))
col2.metric(f"Estado líder ({metrica.lower()})", lider["uf"])
col3.metric(f"Observação humana em {periodo[1]}", numero_br(pct_humana, 1) + "%",
            help="Parte dos registros do ano feita por pessoas (ex.: apps de ciência cidadã).")
col4.metric("Registros com estado reconhecido", numero_br(relatorio["pct_registros_reconhecidos"], 1) + "%",
            help="Depois da limpeza dos nomes de estado (veja a aba Qualidade dos dados).")

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs(
    ["📈 Evolução", "🗺️ Estados", "🐦 Grupos de animais", "🐆 Espécies ameaçadas", "📍 Jundiaí em foco",
     "🧹 Qualidade dos dados"])

#aba 1
with aba1:
    st.subheader("Como cresceram os registros e quem os produz?")
    col_a, col_b = st.columns(2)

    #gráfico de linha. registros por ano
    por_ano = filtrado.groupby("ano", as_index=False)["registros"].sum()
    grafico = px.line(por_ano, x="ano", y="registros", markers=True,
                      labels={"ano": "Ano", "registros": "Registros"}, title=f"Registros por ano ({regiao})")
    col_a.plotly_chart(grafico, width="stretch")

    #% de cada tipo de registro por ano
    tipos_periodo = tipos[(tipos["ano"] >= periodo[0]) & (tipos["ano"] <= periodo[1])]
    grafico = px.bar(tipos_periodo, x="ano", y="pct_do_ano", color="tipo",
                     labels={"ano": "Ano", "pct_do_ano": "% dos registros do ano", "tipo": "Tipo de registro"},
                     title="Tipo de registro (% do ano, Brasil todo)")
    col_b.plotly_chart(grafico, width="stretch")

    #texto automático montado com os números filtrados
    if len(por_ano) >= 2:
        primeiro, ultimo = por_ano.iloc[0], por_ano.iloc[-1]
        crescimento = ultimo["registros"] / primeiro["registros"]
        st.info(
            f"De {primeiro['ano']} a {ultimo['ano']}, os registros por ano passaram de "
            f"{numero_br(primeiro['registros'])} para {numero_br(ultimo['registros'])} "
            f"({numero_br(crescimento, 1)} vezes mais). No último ano, {numero_br(pct_humana, 1)}% dos registros "
            "foram observações feitas por pessoas, e não espécimes guardados em museus."
        )

#aba 2
with aba2:
    st.subheader("O registro de animais é igual em todos os estados?")
    st.write(f"Medida escolhida: **{metrica}**, período de {periodo[0]} a {periodo[1]}, {regiao}.")

    # barras com estados ordenados
    grafico = px.bar(por_estado, x="uf", y=metrica, color="regiao",
                     labels={"uf": "Estado", "regiao": "Região"}, title=f"{metrica} por estado")
    st.plotly_chart(grafico, width="stretch")

    #comparação entre regiões
    por_regiao = por_estado.groupby("regiao", as_index=False)[["registros", "area_km2", "populacao"]].sum()
    por_regiao["Total de registros"] = por_regiao["registros"]
    por_regiao["Registros por km²"] = por_regiao["registros"] / por_regiao["area_km2"]
    por_regiao["Registros por 1.000 habitantes"] = por_regiao["registros"] / por_regiao["populacao"] * 1000
    por_regiao = por_regiao.sort_values(metrica, ascending=False)
    grafico = px.bar(por_regiao, x="regiao", y=metrica, color="regiao", text_auto=".3s",
                     labels={"regiao": "Região"}, title=f"{metrica} por região")
    grafico.update_layout(showlegend=False)
    st.plotly_chart(grafico, width="stretch")
    if len(por_regiao) >= 2 and metrica != "Total de registros":
        primeira, ultima = por_regiao.iloc[0], por_regiao.iloc[-1]
        st.info(
            f"Na medida '{metrica}', o **{primeira['regiao']}** tem {numero_br(primeira[metrica], 2)} "
            f"e o **{ultima['regiao']}** tem {numero_br(ultima[metrica], 2)}: "
            f"{numero_br(primeira[metrica] / ultima[metrica], 1)} vezes menos."
        )

    grafico = px.scatter(por_estado, x="populacao", y="registros", text="uf", color="regiao",
                         log_x=True, log_y=True,
                         labels={"populacao": "População (escala log)", "registros": "Registros (escala log)",
                                 "regiao": "Região"},
                         title="Estados mais populosos têm mais registros?")
    grafico.update_traces(textposition="top center")
    st.plotly_chart(grafico, width="stretch")

    if len(por_estado) >= 3:
        correlacao = np.corrcoef(np.log10(por_estado["populacao"]), np.log10(por_estado["registros"]))[0, 1]
        maior = por_estado.iloc[0]
        menor = por_estado.iloc[-1]
        st.info(
            f"Na medida '{metrica}', **{maior['nome']}** lidera e **{menor['nome']}** fica em último. "
            f"A correlação entre população e número de registros (em escala log) é **{numero_br(correlacao, 2)}**: "
            "quanto mais perto de 1, mais o registro acompanha onde as pessoas moram. "
            "Mais registros não quer dizer mais animais, e sim mais gente observando."
        )

    if len(por_estado) >= 4:
        mediana_km2 = por_estado["Registros por km²"].median()
        mediana_hab = por_estado["Registros por 1.000 habitantes"].median()
        cegos = por_estado[(por_estado["Registros por km²"] < mediana_km2)
                           & (por_estado["Registros por 1.000 habitantes"] < mediana_hab)]
        cegos = cegos.sort_values("Registros por km²")
        if not cegos.empty:
            st.warning(
                f"**Pontos cegos ({len(cegos)} estados):** {', '.join(cegos['nome'])}. "
                "Estão abaixo da mediana tanto em registros por km² quanto por 1.000 habitantes: "
                "faltam observações mesmo considerando o tamanho e a população."
            )

#aba3
with aba3:
    st.subheader("Quais animais são mais registrados?")
    col_a, col_b = st.columns(2)

    grupos_regiao = grupos if regiao == "Brasil todo" else grupos[grupos["regiao"] == regiao]
    por_grupo = grupos_regiao.groupby("grupo", as_index=False)["registros"].sum().sort_values("registros")
    grafico = px.bar(por_grupo, x="registros", y="grupo", orientation="h",
                     labels={"registros": "Registros", "grupo": ""}, title=f"Registros por grupo ({regiao}, 2000-2025)")
    col_a.plotly_chart(grafico, width="stretch")

    #o grupo escolhido no dropdown
    do_grupo = grupos_regiao[grupos_regiao["grupo"] == grupo].sort_values("registros", ascending=False)
    grafico = px.bar(do_grupo, x="uf", y="registros", labels={"uf": "Estado", "registros": "Registros"},
                     title=f"{grupo}: registros por estado")
    col_b.plotly_chart(grafico, width="stretch")

    pct_aves = 100 * por_grupo.loc[por_grupo["grupo"] == "Aves", "registros"].sum() / por_grupo["registros"].sum()
    st.info(
        f"As **aves** são {numero_br(pct_aves, 0)}% dos registros dos grupos analisados ({regiao}). "
        "Provavelmente reflete a popularidade da observação de aves (ex.: app eBird): "
        "os dados mostram o que as pessoas observam, não quantos animais existem."
    )
    st.caption("Este gráfico usa o período 2000-2025 inteiro (não responde ao slider).")

    #sazonalidade
    st.subheader(f"Em que meses os registros de {grupo.lower()} acontecem?")
    saz = dados["sazonalidade_grupo_mes"]
    saz_grupo = saz[saz["grupo"] == grupo].sort_values("mes")
    grafico = px.line(saz_grupo, x="mes_nome", y="pct_do_ano", markers=True,
                      labels={"mes_nome": "Mês", "pct_do_ano": "% dos registros do ano"},
                      title=f"{grupo}: % dos registros em cada mês (Brasil, 2000-2025)")
    grafico.add_hline(y=100 / 12, line_dash="dot", annotation_text="todos os meses iguais",
                      annotation_position="top left")
    st.plotly_chart(grafico, width="stretch")

    if not saz_grupo.empty:
        pico = saz_grupo.loc[saz_grupo["pct_do_ano"].idxmax()]
        vale = saz_grupo.loc[saz_grupo["pct_do_ano"].idxmin()]
        st.info(
            f"**{grupo}:** o mês com mais registros é **{pico['mes_nome']}** ({numero_br(pico['pct_do_ano'], 1)}% do ano) "
            f"e o com menos é **{vale['mes_nome']}** ({numero_br(vale['pct_do_ano'], 1)}%). "
            "Parte da diferença vem do comportamento dos animais (chuvas, reprodução, migração) "
            "e parte de quando as pessoas saem para observar (férias, clima)."
        )


#aba 4
with aba4:
    st.subheader("Onde estão registradas as espécies ameaçadas de extinção?")
    ameacadas_regiao = ameacadas if regiao == "Brasil todo" else ameacadas[ameacadas["regiao"] == regiao]
    #ordem dos estados
    ordem = ameacadas_regiao.groupby("uf")["registros"].sum().sort_values(ascending=False).index.tolist()
    grafico = px.bar(ameacadas_regiao, x="uf", y="registros", color="categoria_nome",
                     category_orders={"uf": ordem,
                                      "categoria_nome": ["Criticamente em perigo", "Em perigo", "Vulnerável"]},
                     color_discrete_map={"Criticamente em perigo": "#8b0000", "Em perigo": "#e4572e",
                                         "Vulnerável": "#f2b134"},
                     labels={"uf": "Estado", "registros": "Registros", "categoria_nome": "Categoria (IUCN)"},
                     title=f"Registros de espécies ameaçadas por estado ({regiao}, 2000-2025)")
    st.plotly_chart(grafico, width="stretch")

    if ordem:
        cr = ameacadas_regiao[ameacadas_regiao["categoria"] == "CR"].sort_values("registros", ascending=False)
        texto = f"O estado com mais registros de espécies ameaçadas é **{ordem[0]}**."
        if not cr.empty:
            texto += f" Para espécies **criticamente em perigo**, o destaque é **{cr.iloc[0]['uf']}**."
        st.info(texto)
    st.caption("Categorias da Lista Vermelha da IUCN. Este gráfico usa o período 2000-2025 inteiro.")

    #5 mais registradas de cada categoria
    st.subheader("Quais espécies ameaçadas são mais registradas no Brasil?")
    especies_br = dados["especies_ameacadas"]
    especies_br = especies_br[especies_br["local"] == "Brasil"].copy()
    #rótulo do gráfico
    especies_br["nome_popular"] = especies_br["nome_popular"].fillna("")
    especies_br["especie"] = especies_br["nome_popular"].where(especies_br["nome_popular"] != "",
                                                                especies_br["nome_cientifico"])
    grafico = px.bar(especies_br.sort_values("registros"), x="registros", y="especie", color="categoria_nome",
                     orientation="h", log_x=True,
                     color_discrete_map={"Criticamente em perigo": "#8b0000", "Em perigo": "#e4572e",
                                         "Vulnerável": "#f2b134"},
                     hover_data=["nome_cientifico", "classe_pt"],
                     labels={"registros": "Registros (escala log)", "especie": "", "categoria_nome": "Categoria"},
                     title="As 5 espécies mais registradas de cada categoria (Brasil, 2000-2025)")
    st.plotly_chart(grafico, width="stretch")
    maior = especies_br.loc[especies_br["registros"].idxmax()]
    st.info(
        f"A espécie ameaçada mais registrada é **{maior['especie']}** (*{maior['nome_cientifico']}*), "
        f"com {numero_br(maior['registros'])} registros. A escala é logarítmica porque ela tem muito mais "
        f"registros que as outras: poucas espécies concentram a maior parte dos dados."
    )
#aba5
with aba5:
    st.subheader("E em Jundiaí, quem observa os animais?")
    st.write("Os mesmos dados do GBIF, filtrados pelo município de Jundiaí-SP e comparados com o Brasil "
             "e com as cidades vizinhas (2000-2025).")

    j_grupos = dados["jundiai_grupos"]
    j_tipo = dados["jundiai_tipo"]
    j_fontes = dados["jundiai_fontes"]
    cidades = dados["cidades_regiao"]
    jundiai = cidades[cidades["cidade"] == "Jundiaí"].iloc[0]
    insetos = j_grupos[j_grupos["grupo"] == "Insetos"].iloc[0]

    #registros por km² do estado de SP no mesmo período
    sp = estado_ano[estado_ano["uf"] == "SP"]
    sp_por_km2 = sp["registros"].sum() / sp["area_km2"].iloc[0]

    #KPIs de Jundiaí
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros em Jundiaí", numero_br(jundiai["registros"]))
    c2.metric("Registros por km²", numero_br(jundiai["por_km2"], 1),
              help=f"Estado de São Paulo no mesmo período: {numero_br(sp_por_km2, 1)} por km².")
    c3.metric("Insetos (% dos registros)", numero_br(insetos["pct_jundiai"], 1) + "%",
              help=f"No Brasil: {numero_br(insetos['pct_brasil'], 1)}%.")
    pct_museu = j_tipo.loc[j_tipo["tipo"] == "Espécime de museu", "pct"].sum()
    c4.metric("Espécimes de museu", numero_br(pct_museu, 1) + "%",
              help="Animais coletados e guardados em coleções científicas.")

    col_a, col_b = st.columns(2)
    #registros por ano em Jundiaí
    j_ano = dados["jundiai_ano"]
    j_ano = j_ano[(j_ano["ano"] >= periodo[0]) & (j_ano["ano"] <= periodo[1])]
    grafico = px.bar(j_ano, x="ano", y="registros", labels={"ano": "Ano", "registros": "Registros"},
                     title="Registros por ano em Jundiaí")
    col_a.plotly_chart(grafico, width="stretch")

    #transforma as colunas pct_jundiai e pct_brasil em linhas,
    comparacao = j_grupos.melt(id_vars="grupo", value_vars=["pct_jundiai", "pct_brasil"],
                               var_name="local", value_name="pct")
    comparacao["local"] = comparacao["local"].map({"pct_jundiai": "Jundiaí", "pct_brasil": "Brasil"})
    grafico = px.bar(comparacao, x="grupo", y="pct", color="local", barmode="group",
                     labels={"grupo": "", "pct": "% dos registros", "local": ""},
                     title="Grupos de animais: Jundiaí x Brasil")
    col_b.plotly_chart(grafico, width="stretch")

    st.info(
        f"**Por que tantos insetos?** {numero_br(insetos['pct_jundiai'], 1)}% dos registros de Jundiaí são insetos, "
        f"contra {numero_br(insetos['pct_brasil'], 1)}% no Brasil. Dos {numero_br(insetos['registros'])} registros de insetos, "
        f"{numero_br(insetos['registros_no_local'])} citam a **{insetos['local_mais_citado']}**: "
        "a cidade tem uma área protegida estudada por pesquisadores."
    )

    col_a, col_b = st.columns(2)
    coluna_cidade = {"Total de registros": "registros", "Registros por km²": "por_km2",
                     "Registros por 1.000 habitantes": "por_mil_hab"}[metrica]
    cidades = cidades.sort_values(coluna_cidade, ascending=False)
    grafico = px.bar(cidades, x="cidade", y=coluna_cidade, labels={"cidade": "", coluna_cidade: metrica},
                     title=f"Jundiaí e cidades vizinhas: {metrica.lower()}")
    col_a.plotly_chart(grafico, width="stretch")

    grafico = px.bar(j_fontes.sort_values("registros"), x="registros", y="fonte", orientation="h",
                     labels={"registros": "Registros", "fonte": ""}, title="Quem publicou os dados de Jundiaí")
    col_b.plotly_chart(grafico, width="stretch")

    menor = cidades.sort_values("por_mil_hab").iloc[0]
    st.info(
        f"**Ponto cego vizinho:** {menor['cidade']} tem {numero_br(menor['populacao'])} habitantes e só "
        f"{numero_br(menor['registros'])} registros ({numero_br(menor['por_mil_hab'], 1)} por 1.000 habitantes), "
        f"contra {numero_br(jundiai['por_mil_hab'], 1)} em Jundiaí. "
        f"Em Jundiaí, {numero_br(j_fontes.iloc[0]['pct'], 0)}% dos registros vêm de uma única fonte "
        f"({j_fontes.iloc[0]['fonte']}) e {numero_br(j_fontes.iloc[1]['pct'], 0)}% de outra "
        f"({j_fontes.iloc[1]['fonte']})."
    )

    st.write("**Espécies ameaçadas registradas em Jundiaí:**")
    especies_j = dados["especies_ameacadas"]
    especies_j = especies_j[especies_j["local"] == "Jundiaí"].sort_values("registros", ascending=False)
    especies_j["nome_popular"] = especies_j["nome_popular"].fillna("")
    if especies_j.empty:
        st.write("Nenhum registro de espécie ameaçada no período.")
    else:
        #nomes viram links
        especies_j["nome_popular"] = especies_j["nome_popular"].apply(link_google)
        especies_j["nome_cientifico"] = especies_j["nome_cientifico"].apply(link_google)
        st.dataframe(especies_j[["nome_popular", "nome_cientifico", "classe_pt", "categoria_nome", "registros"]],
                     hide_index=True,
                     column_config={"nome_popular": coluna_link("Nome popular"),
                                    "nome_cientifico": coluna_link("Nome científico"),
                                    "classe_pt": "Grupo", "categoria_nome": "Categoria", "registros": "Registros"})
        st.caption("Espécies com 1 só registro merecem cuidado: podem ser erro de identificação "
                   "ou um animal fora da natureza (de estimação, por exemplo).")

    st.write("**As 10 espécies mais registradas em Jundiaí:**")
    mais_registradas = dados["jundiai_especies"].copy()
    mais_registradas["nome_cientifico"] = mais_registradas["nome_cientifico"].apply(link_google)
    mais_registradas["nome_popular"] = mais_registradas["nome_popular"].fillna("").apply(link_google)
    st.dataframe(mais_registradas, hide_index=True,
                 column_config={"nome_cientifico": coluna_link("Nome científico"),
                                "nome_popular": coluna_link("Nome popular"), "registros": "Registros"})

    #beija-flores de jundiaí
    st.subheader("Beija-flores de Jundiaí")
    beija_flores = dados["beija_flores_jundiai"].copy()
    beija_flores["nome_popular"] = beija_flores["nome_popular"].fillna("")
    mais_comum = beija_flores.iloc[0]
    st.info(
        f"Jundiaí tem **{numero_br(beija_flores['registros'].sum())} registros** de beija-flores, de "
        f"**{len(beija_flores)} espécies** diferentes. O mais registrado é o **{mais_comum['nome_popular']}** "
        f"(*{mais_comum['nome_cientifico']}*), com {numero_br(mais_comum['pct'], 1)}% dos registros."
    )
    #imagem no canto e tabela ao lado
    col_foto, col_tabela = st.columns([1, 3], vertical_alignment="center")
    col_foto.image(BEIJA_FLOR, width="stretch")
    beija_flores["nome_popular"] = beija_flores["nome_popular"].apply(link_google)
    beija_flores["nome_cientifico"] = beija_flores["nome_cientifico"].apply(link_google)
    col_tabela.dataframe(beija_flores, hide_index=True,
                         column_config={"nome_popular": coluna_link("Nome popular"),
                                        "nome_cientifico": coluna_link("Nome científico"),
                                        "registros": "Registros", "pct": st.column_config.NumberColumn(
                                            "% dos beija-flores", format="%.1f%%")})

#aba 6
with aba6:
    st.subheader("O que fizemos para limpar os dados?")
    st.write(
        "No GBIF, o nome do estado é **texto livre**: cada instituição escreve de um jeito "
        "('São Paulo', 'Sao Paulo', 'SP', 'Estado de São Paulo'...). Padronizados para a sigla da UF."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Grafias diferentes de estado (antes)", numero_br(relatorio["grafias_de_estado_antes"]))
    c2.metric("Estados depois da limpeza", relatorio["ufs_depois"])
    c3.metric("Registros sem nenhum estado informado", numero_br(relatorio["pct_registros_sem_estado"], 1) + "%")

    total_ano_f = total_ano[(total_ano["ano"] >= periodo[0]) & (total_ano["ano"] <= periodo[1])].copy()
    total_ano_f["% sem estado"] = 100 * total_ano_f["sem_uf"] / total_ano_f["total"]
    grafico = px.bar(total_ano_f, x="ano", y="% sem estado", labels={"ano": "Ano"},
                     title="% de registros sem estado informado, por ano (Brasil todo)")
    st.plotly_chart(grafico, width="stretch")
    st.caption("Esses registros entram no total do Brasil, mas não aparecem nos gráficos por estado.")


#tabels
if mostrar_tabelas:
    st.header("Tabelas de dados")
    st.write("Registros por estado no período e região escolhidos:")
    tabela_estados = por_estado[["uf", "nome", "regiao", "registros", "populacao", "area_km2",
                                 "Registros por km²", "Registros por 1.000 habitantes"]].round(2)
    tabela_estados["nome"] = tabela_estados["nome"].apply(link_google)
    st.dataframe(tabela_estados, hide_index=True, column_config={"nome": coluna_link("Estado")})




















