#Tratamento

import json
import os

import pandas as pd

PASTA_ETAPA = os.path.dirname(os.path.abspath(__file__))
PASTA_ENTRADA = os.path.join(PASTA_ETAPA, "dados_brutos")
PASTA_SAIDA = os.path.join(PASTA_ETAPA, "dados_tratados")

#estados
ESTADOS = {
    "AC": ("Acre", "Norte", 12), "AL": ("Alagoas", "Nordeste", 27),
    "AP": ("Amapá", "Norte", 16), "AM": ("Amazonas", "Norte", 13),
    "BA": ("Bahia", "Nordeste", 29), "CE": ("Ceará", "Nordeste", 23),
    "DF": ("Distrito Federal", "Centro-Oeste", 53), "ES": ("Espírito Santo", "Sudeste", 32),
    "GO": ("Goiás", "Centro-Oeste", 52), "MA": ("Maranhão", "Nordeste", 21),
    "MT": ("Mato Grosso", "Centro-Oeste", 51), "MS": ("Mato Grosso do Sul", "Centro-Oeste", 50),
    "MG": ("Minas Gerais", "Sudeste", 31), "PA": ("Pará", "Norte", 15),
    "PB": ("Paraíba", "Nordeste", 25), "PR": ("Paraná", "Sul", 41),
    "PE": ("Pernambuco", "Nordeste", 26), "PI": ("Piauí", "Nordeste", 22),
    "RJ": ("Rio de Janeiro", "Sudeste", 33), "RN": ("Rio Grande do Norte", "Nordeste", 24),
    "RS": ("Rio Grande do Sul", "Sul", 43), "RO": ("Rondônia", "Norte", 11),
    "RR": ("Roraima", "Norte", 14), "SC": ("Santa Catarina", "Sul", 42),
    "SP": ("São Paulo", "Sudeste", 35), "SE": ("Sergipe", "Nordeste", 28),
    "TO": ("Tocantins", "Norte", 17),
}

#traduções
TIPOS_REGISTRO = {
    "HUMAN_OBSERVATION": "Observação humana",
    "PRESERVED_SPECIMEN": "Espécime de museu",
    "MACHINE_OBSERVATION": "Câmera / sensor",
    "MATERIAL_SAMPLE": "Outros",
    "MATERIAL_CITATION": "Outros",
    "LIVING_SPECIMEN": "Outros",
    "FOSSIL_SPECIMEN": "Outros",
    "OCCURRENCE": "Outros",
}

#ameaças
CATEGORIAS = {"CR": "Criticamente em perigo", "EN": "Em perigo", "VU": "Vulnerável"}

#nomes populares - Jundiaí / especies ameaçadas mais registradas
NOMES_POPULARES = {
    "Pitangus sulphuratus": "Bem-te-vi",
    "Thraupis sayaca": "Sanhaço-cinzento",
    "Aratinga leucophthalma": "Periquitão",
    "Patagioenas picazuro": "Pombão (asa-branca)",
    "Coragyps atratus": "Urubu-preto",
    "Notiochelidon cyanoleuca": "Andorinha-pequena-de-casa",
    "Troglodytes musculus": "Corruíra",
    "Zenaida auriculata": "Avoante (pomba-de-bando)",
    "Passer domesticus": "Pardal",
    "Furnarius rufus": "João-de-barro",
    "Trichechus manatus": "Peixe-boi",
    "Crax fasciolata": "Mutum-de-penacho",
    "Anodorhynchus hyacinthinus": "Arara-azul",
    "Tringa flavipes": "Maçarico-de-perna-amarela",
    "Penelope ochrogaster": "Jacu-de-barriga-castanha",
    "Amazona vinacea": "Papagaio-de-peito-roxo",
    "Pipile jacutinga": "Jacutinga",
    "Scarus trispinosus": "Budião-azul",
    "Eretmochelys imbricata": "Tartaruga-de-pente",
    "Mergus octosetaceus": "Pato-mergulhão",
    "Leopardus tigrinus": "Gato-do-mato-pequeno",
    "Leopardus guttulus": "Gato-do-mato-pequeno-do-sul",
    "Sporophila frontalis": "Pixoxó",
    "Myrmecophaga tridactyla": "Tamanduá-bandeira",
    "Tayassu pecari": "Queixada",
    "Callithrix aurita": "Sagui-da-serra-escuro",
    "Sylvilagus brasiliensis": "Tapiti",
    "Mesocricetus auratus": "Hamster-dourado",
    #beija-flores de jundiaí
    "Eupetomena macroura": "Beija-flor-tesoura",
    "Thalurania glaucopis": "Beija-flor-de-fronte-violeta",
    "Chlorostilbon lucidus": "Besourinho-de-bico-vermelho",
    "Phaethornis pretrei": "Rabo-branco-acanelado",
    "Leucochloris albicollis": "Beija-flor-de-papo-branco",
    "Florisuga fusca": "Beija-flor-preto",
    "Chionomesa lactea": "Beija-flor-de-peito-azul",
    "Phaethornis eurynome": "Rabo-branco-de-garganta-rajada",
    "Chrysuronia versicolor": "Beija-flor-de-banda-branca",
    "Calliphlox amethystina": "Estrelinha-ametista",
    "Anthracothorax nigricollis": "Beija-flor-de-veste-preta",
    "Colibri serrirostris": "Beija-flor-de-orelha-violeta",
    "Heliomaster squamosus": "Bico-reto-de-banda-branca",
    "Lophornis chalybeus": "Topetinho-verde",
    "Chionomesa fimbriata": "Beija-flor-de-garganta-verde",
    "Eupetomena cirrochloris": "Beija-flor-cinza",
    "Heliothryx auritus": "Beija-flor-de-bochecha-azul",
    "Chlorestes cyanus": "Beija-flor-roxo",
    "Phaethornis ruber": "Rabo-branco-rubro",
    "Clytolaema rubricauda": "Beija-flor-rubi",
}

#clasees das especies traduzidas
CLASSES_PT = {
    "Aves": "Aves", "Mammalia": "Mamíferos", "Amphibia": "Anfíbios", "Insecta": "Insetos",
    "Squamata": "Lagartos e serpentes", "Testudines": "Tartarugas", "Crocodylia": "Jacarés",
    "Anthozoa": "Corais", "Gastropoda": "Caramujos",
}

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

#nomes curtos para as instituições
NOMES_FONTES = {
    "eBird": "eBird (app de aves)",
    "UFSCar": "Coleção da UFSCar (insetos)",
    "SISBio": "ICMBio (pesquisas autorizadas)",
    "iNaturalist": "iNaturalist (app)",
    "MZUSP": "Museu de Zoologia da USP (borboletas e mariposas)",
}

#funções
def ler_json(nome_arquivo):
    #abre um .json da pasta dados_brutos
    with open(os.path.join(PASTA_ENTRADA, nome_arquivo), encoding="utf-8") as arquivo:
        return json.load(arquivo)

def salvar_csv(tabela, nome_arquivo):
    #salva a tabela como .csv na pasta dados_tratados
    tabela.to_csv(os.path.join(PASTA_SAIDA, nome_arquivo), index=False, encoding="utf-8")
    print(f"   salvo: {nome_arquivo} ({len(tabela)} linhas)")
#padronização
def simplificar(textos):
    return (
        textos.astype(str)
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("ascii")
        .str.lower()
        .str.replace(r"^(estado de|estado do|estado da|state of)\s+", "", regex=True)
        .str.replace(r"\s+(state|estado)$", "", regex=True)
        .str.strip()                              # tira espaços das pontas
    )

DE_PARA = {}
for sigla, (nome, regiao, codigo) in ESTADOS.items():
    DE_PARA[simplificar(pd.Series([nome]))[0]] = sigla
    DE_PARA[sigla.lower()] = sigla
DE_PARA["brasilia"] = "DF"
DE_PARA["federal district"] = "DF"

def padronizar_estado(tabela):
    tabela["uf"] = simplificar(tabela["estado"]).map(DE_PARA)
    return tabela

def facet_para_tabela(lista_de_contagens, **colunas_extras):
    tabela = pd.DataFrame(lista_de_contagens).rename(columns={"name": "estado", "count": "registros"})
    for coluna, valor in colunas_extras.items():
        tabela[coluna] = valor
    return tabela

def ler_ibge(nome_arquivo):
    linhas = []
    for variavel in ler_json(nome_arquivo):
        nome_coluna = "populacao" if variavel["id"] == "93" else "area_km2"
        for serie in variavel["resultados"][0]["series"]:
            linhas.append({
                "codigo_ibge": int(serie["localidade"]["id"]),
                "variavel": nome_coluna,
                "valor": float(serie["serie"]["2022"]),
            })
    #transforma as linhas "variavel/valor" em duas colunas (populacao e area_km2)
    return pd.DataFrame(linhas).pivot(index="codigo_ibge", columns="variavel", values="valor").reset_index()
def nome_curto(titulo):
    #nome curto da instituição (ou o título cortado, se não estiver na lista)
    for trecho, nome in NOMES_FONTES.items():
        if trecho in titulo:
            return nome
    return titulo[:40]

#main

def main():
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    relatorio = {}  #guarda os números do antes e depois da limpeza
    #a limpeza dos nomes de estado
    print("1) Registros por ano e estado")
    dados_ano = ler_json("gbif_registros_por_ano.json")
    estado_ano = pd.concat([facet_para_tabela(item["por_estado"], ano=item["ano"]) for item in dados_ano],
                           ignore_index=True)
    estado_ano = padronizar_estado(estado_ano)

    nao_reconhecidos = (estado_ano[estado_ano["uf"].isna()]
                        .groupby("estado")["registros"].sum()
                        .sort_values(ascending=False).reset_index())
    salvar_csv(nao_reconhecidos, "estados_nao_reconhecidos.csv")
    relatorio["grafias_de_estado_antes"] = int(estado_ano["estado"].nunique())
    relatorio["ufs_depois"] = int(estado_ano["uf"].nunique())
    reconhecidos = estado_ano.loc[estado_ano["uf"].notna(), "registros"].sum()
    relatorio["pct_registros_reconhecidos"] = float(round(100 * reconhecidos / estado_ano["registros"].sum(), 2))

    estado_ano = estado_ano.dropna(subset=["uf"]).groupby(["ano", "uf"], as_index=False)["registros"].sum()

    totais = pd.DataFrame([{"ano": item["ano"], "total": item["total"]} for item in dados_ano])
    soma_ufs = estado_ano.groupby("ano")["registros"].sum().reset_index(name="com_uf")
    totais = totais.merge(soma_ufs, on="ano")
    totais["sem_uf"] = totais["total"] - totais["com_uf"]
    relatorio["pct_registros_sem_estado"] = float(round(100 * totais["sem_uf"].sum() / totais["total"].sum(), 2))
    salvar_csv(totais, "total_por_ano.csv")

    #junta com população e área
    print("2) População e área dos estados (IBGE)")
    info_estados = pd.DataFrame(
        [{"uf": s, "nome": n, "regiao": r, "codigo_ibge": c} for s, (n, r, c) in ESTADOS.items()])
    info_estados = info_estados.merge(ler_ibge("ibge_estados.json"), on="codigo_ibge")
    salvar_csv(info_estados, "estados_ibge.csv")

    estado_ano = estado_ano.merge(info_estados, on="uf")
    salvar_csv(estado_ano, "registros_estado_ano.csv")

    #tipo de registro por ano, em português e em % do ano
    print("3) Tipo de registro por ano")
    tipos = pd.concat([pd.DataFrame(item["por_tipo"]).assign(ano=item["ano"]) for item in dados_ano],
                      ignore_index=True)
    tipos["tipo"] = tipos["name"].map(TIPOS_REGISTRO).fillna("Outros")
    tipos = tipos.groupby(["ano", "tipo"], as_index=False)["count"].sum().rename(columns={"count": "registros"})
    tipos["pct_do_ano"] = (100 * tipos["registros"] / tipos.groupby("ano")["registros"].transform("sum")).round(2)
    salvar_csv(tipos, "tipo_registro_ano.csv")

    #animais por estado
    print("4) Grupos de animais por estado")
    grupos = pd.concat([facet_para_tabela(g["por_estado"], grupo=g["grupo"]) for g in ler_json("gbif_grupos.json")])
    grupos = padronizar_estado(grupos).dropna(subset=["uf"])
    grupos = grupos.groupby(["grupo", "uf"], as_index=False)["registros"].sum()
    grupos = grupos.merge(info_estados[["uf", "regiao"]], on="uf")
    salvar_csv(grupos, "grupos_estado.csv")

    #espécies ameaçadas por estado
    print("5) Espécies ameaçadas por estado")
    ameacadas = pd.concat([facet_para_tabela(a["por_estado"], categoria=a["categoria"])
                           for a in ler_json("gbif_ameacadas.json")])
    ameacadas = padronizar_estado(ameacadas).dropna(subset=["uf"])
    ameacadas = ameacadas.groupby(["categoria", "uf"], as_index=False)["registros"].sum()
    ameacadas["categoria_nome"] = ameacadas["categoria"].map(CATEGORIAS)
    ameacadas = ameacadas.merge(info_estados[["uf", "regiao"]], on="uf")
    salvar_csv(ameacadas, "ameacadas_estado.csv")

    #Jundiaí em foco
    print("6) Jundiaí")
    jundiai = ler_json("gbif_jundiai.json")

    #registros por ano
    por_ano = pd.DataFrame(jundiai["por_ano"]).rename(columns={"name": "ano", "count": "registros"})
    por_ano["ano"] = por_ano["ano"].astype(int)
    salvar_csv(por_ano.sort_values("ano"), "jundiai_ano.csv")

    #tipo de registro, em %
    tipos_j = pd.DataFrame(jundiai["por_tipo"])
    tipos_j["tipo"] = tipos_j["name"].map(TIPOS_REGISTRO).fillna("Outros")
    tipos_j = tipos_j.groupby("tipo", as_index=False)["count"].sum().rename(columns={"count": "registros"})
    tipos_j["pct"] = (100 * tipos_j["registros"] / tipos_j["registros"].sum()).round(1)
    salvar_csv(tipos_j, "jundiai_tipo.csv")

    #% em Jundiaí comparado com o % no Brasil
    grupos_j = pd.DataFrame(jundiai["por_grupo"])
    grupos_j["pct_jundiai"] = (100 * grupos_j["registros"] / grupos_j["registros"].sum()).round(1)
    brasil = grupos.groupby("grupo")["registros"].sum()
    grupos_j["pct_brasil"] = grupos_j["grupo"].map(100 * brasil / brasil.sum()).round(1)
    salvar_csv(grupos_j, "jundiai_grupos.csv")

    #espécies mais registradas, com nome popular
    especies = pd.DataFrame(jundiai["especies"]).rename(columns={"count": "registros"})
    especies["nome_popular"] = especies["nome_cientifico"].map(NOMES_POPULARES).fillna("")
    salvar_csv(especies[["nome_cientifico", "nome_popular", "registros"]], "jundiai_especies.csv")

    #quem publicou os dados, com nome curto e %
    fontes = pd.DataFrame(jundiai["fontes"]).rename(columns={"count": "registros"})
    fontes["pct"] = (100 * fontes["registros"] / jundiai["total"]).round(1)
    fontes["fonte"] = fontes["titulo"].map(nome_curto)
    salvar_csv(fontes[["fonte", "titulo", "registros", "pct"]], "jundiai_fontes.csv")

    #cidades vizinhas
    cidades = pd.DataFrame(ler_json("gbif_cidades.json")).merge(ler_ibge("ibge_cidades.json"), on="codigo_ibge")
    cidades["por_km2"] = (cidades["registros"] / cidades["area_km2"]).round(2)
    cidades["por_mil_hab"] = (cidades["registros"] / cidades["populacao"] * 1000).round(2)
    salvar_csv(cidades, "cidades_regiao.csv")
    relatorio["jundiai_total"] = int(jundiai["total"])

    #% dos registros de cada grupo em cada mês
    print("7) Sazonalidade")
    sazonalidade = pd.concat([pd.DataFrame(s["por_mes"]).assign(grupo=s["grupo"])
                              for s in ler_json("gbif_sazonalidade.json")], ignore_index=True)
    sazonalidade = sazonalidade.rename(columns={"name": "mes", "count": "registros"})
    sazonalidade["mes"] = sazonalidade["mes"].astype(int)
    sazonalidade = sazonalidade[sazonalidade["mes"].between(1, 12)]
    sazonalidade["mes_nome"] = sazonalidade["mes"].map(lambda m: MESES[m - 1])
    sazonalidade["pct_do_ano"] = (100 * sazonalidade["registros"]
                                  / sazonalidade.groupby("grupo")["registros"].transform("sum")).round(2)
    salvar_csv(sazonalidade.sort_values(["grupo", "mes"]), "sazonalidade_grupo_mes.csv")

    #espécies ameaçadas mais registradas (Brasil/Jundiaí)
    print("8) Espécies ameaçadas")
    linhas = []
    for bloco in ler_json("gbif_especies_ameacadas.json"):
        for especie in bloco["especies"]:
            linhas.append({
                "local": bloco["local"],
                "categoria": bloco["categoria"],
                "nome_cientifico": especie["nome_cientifico"],
                "classe": especie["classe"],
                "registros": especie["count"],
            })
    especies_ameacadas = pd.DataFrame(linhas)
    especies_ameacadas["categoria_nome"] = especies_ameacadas["categoria"].map(CATEGORIAS)
    especies_ameacadas["nome_popular"] = especies_ameacadas["nome_cientifico"].map(NOMES_POPULARES).fillna("")
    especies_ameacadas["classe_pt"] = especies_ameacadas["classe"].map(CLASSES_PT).fillna(
        especies_ameacadas["classe"]).fillna("Não informada")
    salvar_csv(especies_ameacadas[["local", "categoria", "categoria_nome", "nome_cientifico", "nome_popular",
                                   "classe_pt", "registros"]], "especies_ameacadas.csv")

    #beija-flores em jundiaí, com o % de cada espécie
    print("9) Beija-flores em Jundiaí")
    dados_beija_flor = ler_json("gbif_beija_flores.json")
    beija_flores = pd.DataFrame(dados_beija_flor["especies"]).rename(columns={"count": "registros"})
    beija_flores["nome_popular"] = beija_flores["nome_cientifico"].map(NOMES_POPULARES).fillna("")
    beija_flores["pct"] = (100 * beija_flores["registros"] / dados_beija_flor["total"]).round(1)
    salvar_csv(beija_flores[["nome_popular", "nome_cientifico", "registros", "pct"]], "beija_flores_jundiai.csv")

    #Relatório da limpeza (aba "Qualidade dos dados")
    with open(os.path.join(PASTA_SAIDA, "relatorio_limpeza.json"), "w", encoding="utf-8") as arquivo:
        json.dump(relatorio, arquivo, ensure_ascii=False, indent=1)
    print("\nRelatório da limpeza:", relatorio)
    print("Tratamento concluído! Próxima etapa: streamlit run 3_dash.py")


if __name__ == "__main__":
    main()