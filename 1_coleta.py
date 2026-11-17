#Coleta de dados - API

import json
import os
import time
import requests

URL_GBIF = "https://api.gbif.org/v1/occurrence/search"
URL_IBGE = "https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93|6318"

PASTA_ETAPA = os.path.dirname(os.path.abspath(__file__))
PASTA_SAIDA =os.path.join(PASTA_ETAPA, "dados_brutos")

ANO_INICIO = 2000
ANO_FIM = 2025
# Filtro usado em TODAS as buscas no GBIF:
#   country = BR > só registros no Brasil
#   taxonKey = 1 > só o reino Animalia (animais)
#   occurrenceStatus  > só registros de presença
FILTRO_BASE = {"country": "BR", "taxonKey": 1, "occurrenceStatus": "PRESENT"}
# os répteis são divididos em lagartos/serpentes, tartarugas e jacarés.
GRUPOS = {
    "Aves": [212],
    "Mamíferos": [359],
    "Répteis": [11592253, 11418114, 11493978],
    "Anfíbios": [131],
    "Insetos": [216],
    "Aracnídeos": [367],
}

CATEGORIAS_AMEACA = ["CR", "EN", "VU"]

#(código do município no GBIF, código no IBGE)
CIDADES = {
    "Jundiaí": ("BRA.25.296_2", 3525904),
    "Várzea Paulista": ("BRA.25.637_2", 3556503),
    "Campo Limpo Paulista": ("BRA.25.110_2", 3509601),
    "Itupeva": ("BRA.25.276_2", 3524006),
    "Louveira": ("BRA.25.311_2", 3527306),
    "Jarinu": ("BRA.25.288_2", 3525201),
    "Cabreúva": ("BRA.25.96_2", 3508405),
}
JUNDIAI = CIDADES ["Jundiaí"][0]

#família dos beija-flores (Trochilidae) no GBIF
FAMILIA_BEIJA_FLOR = 5289

def buscar_gbif (parametros):
    #adicionando limites para trazer somente as contagens
    parametros = {**FILTRO_BASE, **parametros, "limit": 0}
    #pedido
    resposta = requests.get(URL_GBIF, params=parametros, timeout=60)
    #caso erro
    resposta.raise_for_status()
    #para não sobrecarregr a API
    time.sleep(0.2)
    #converte para JSON
    return resposta.json()

def contagens_do_facet(resposta, campo):
    #agrupamento dentro da API
    for facet in resposta["facets"]:
        if facet["field"] == campo:
            return facet["counts"]
    return []

def salvar_json(dados, nome_arquivo):
    caminho=os.path.join(PASTA_SAIDA, nome_arquivo)
    with open(caminho, "w",encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=1)
    print(" salvo", nome_arquivo)

def main():
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    periodo = f"{ANO_INICIO},{ANO_FIM}" #2000 A 2025

    print("1) Registros por ano, estado e tipo de registro")
    registros_ano = []
    for ano in range(ANO_INICIO, ANO_FIM +1):
        resposta = buscar_gbif({
            "year": ano,
            "facet": ["stateProvince", "basisOfRecord"],
            "facetLimit": 1000,
        })
        print(f"  {ano}: {resposta['count']} registros")
        registros_ano.append({
            "ano":ano,
            "total": resposta["count"],
            "por_estado": contagens_do_facet(resposta, "STATE_PROVINCE"),
            "por_tipo": contagens_do_facet(resposta, "BASIS_OF_RECORD"),
        })
    salvar_json(registros_ano, "gbif_registros_por_ano.json")

    print("2) Registros por grupo de animais e estado")
    grupos = []
    for grupo, chaves in GRUPOS.items():
        resposta = buscar_gbif({
            "taxonKey": chaves,
            "year": periodo,
            "facet": "stateProvince",
            "facetLimit": 1000,
        })
        print(f"   {grupo}: {resposta['count']}registros")
        grupos.append({"grupo": grupo, "por_estado": contagens_do_facet(resposta, "STATE_PROVINCE")})
    salvar_json(grupos, "gbif_grupos.json")

    print("3) Registros de espécies ameaçadas por estado")
    ameacadas = []
    for categoria in CATEGORIAS_AMEACA:
        resposta= buscar_gbif({
            "iucnRedListCategory": categoria,
            "year": periodo,
            "facet": "stateProvince",
            "facetLimit": 1000,
        })
        print(f"   {categoria}: {resposta['count']} registros")
        ameacadas.append({"categoria": categoria, "por_estado": contagens_do_facet(resposta, "STATE_PROVINCE")})
    salvar_json(ameacadas, "gbif_ameacadas.json")

    #IBGE
    print("4) População e área dos estados (IBGE)")
    resposta = requests.get(URL_IBGE, params={"localidades": "N3[all]"}, timeout=60)
    resposta.raise_for_status()
    salvar_json(resposta.json(), "ibge_estados.json")

    #jundiaí
    print("5) Jundiaí em foco")
    resposta = buscar_gbif({
        "gadmGid": JUNDIAI,
        "year": periodo,
        "facet": ["year", "basisOfRecord", "speciesKey", "datasetKey"],
        "facetLimit": 30,
    })
    print(f"    Jundiaí: {resposta['count']} registros")
    jundiai = {
        "total": resposta["count"],
        "por_ano": contagens_do_facet(resposta, "YEAR"),
        "por_tipo": contagens_do_facet(resposta, "BASIS_OF_RECORD"),
        "especies": contagens_do_facet(resposta, "SPECIES_KEY")[:10],  # as 10 primeiras
        "fontes": contagens_do_facet(resposta, "DATASET_KEY")[:5],     # as 5 primeiras
        "por_grupo": [],
    }
    #busca pelos nomes
    for especie in jundiai["especies"]:
        dados = requests.get(f"https://api.gbif.org/v1/species/{especie['name']}", timeout=60).json()
        especie["nome_cientifico"] = dados.get("canonicalName")
    for fonte in jundiai["fontes"]:
        dados = requests.get(f"https://api.gbif.org/v1/dataset/{fonte['name']}", timeout=60).json()
        fonte["titulo"] = dados.get("title")

    for grupo, chaves in GRUPOS.items():
        resposta = buscar_gbif({"gadmGid": JUNDIAI, "taxonKey": chaves, "year": periodo,
                                "facet": "locality", "facetLimit": 1})
        local = contagens_do_facet(resposta, "LOCALITY")
        jundiai["por_grupo"].append({
            "grupo": grupo,
            "registros": resposta["count"],
            "local_mais_citado": local[0]["name"] if local else None,
            "registros_no_local": local[0]["count"] if local else 0,
        })
    salvar_json(jundiai, "gbif_jundiai.json")
    #jundiai e cidades vizinhas
    print("6) Cidades vizinhas")
    cidades = []
    for cidade, (codigo_gbif, codigo_ibge) in CIDADES.items():
        resposta = buscar_gbif({"gadmGid": codigo_gbif, "year": periodo})
        print(f"   {cidade}: {resposta['count']} registros")
        cidades.append({"cidade": cidade, "codigo_ibge": codigo_ibge, "registros": resposta["count"]})
    salvar_json(cidades, "gbif_cidades.json")

    codigos = ",".join(str(codigo_ibge) for _, codigo_ibge in CIDADES.values())
    resposta = requests.get(URL_IBGE, params={"localidades": f"N6[{codigos}]"}, timeout=60)
    resposta.raise_for_status()
    salvar_json(resposta.json(), "ibge_cidades.json")
    #meses
    print("7) Sazonalidade (registros por mês)")
    sazonalidade = []
    for grupo, chaves in GRUPOS.items():
        resposta = buscar_gbif({"taxonKey": chaves, "year": periodo, "facet": "month", "facetLimit": 12})
        print(f"   {grupo}")
        sazonalidade.append({"grupo": grupo, "por_mes": contagens_do_facet(resposta, "MONTH")})
    salvar_json(sazonalidade, "gbif_sazonalidade.json")
    #especies em perigo
    print("8) Espécies ameaçadas mais registradas")
    especies_ameacadas = []
    for local, filtro_local, quantas in [("Brasil", {}, 5), ("Jundiaí", {"gadmGid": JUNDIAI}, 10)]:
        for categoria in CATEGORIAS_AMEACA:
            resposta = buscar_gbif({**filtro_local, "iucnRedListCategory": categoria, "year": periodo,
                                    "facet": "speciesKey", "facetLimit": quantas})
            especies = contagens_do_facet(resposta, "SPECIES_KEY")
            # o facet só traz o código; buscamos o nome científico e a classe de cada espécie
            for especie in especies:
                dados = requests.get(f"https://api.gbif.org/v1/species/{especie['name']}", timeout=60).json()
                especie["nome_cientifico"] = dados.get("canonicalName")
                especie["classe"] = dados.get("class")
            print(f"   {local} {categoria}: {resposta['count']} registros, {len(especies)} espécies")
            especies_ameacadas.append({"local": local, "categoria": categoria, "especies": especies})
    salvar_json(especies_ameacadas, "gbif_especies_ameacadas.json")
    #beija-flores em jundiaí
    print("9) Beija-flores em Jundiaí")
    resposta = buscar_gbif({"gadmGid": JUNDIAI, "familyKey": FAMILIA_BEIJA_FLOR, "year": periodo,
                            "facet": "speciesKey", "facetLimit": 50})
    beija_flores = {"total": resposta["count"], "especies": contagens_do_facet(resposta, "SPECIES_KEY")}
    #busca pelos nomes
    for especie in beija_flores["especies"]:
        dados = requests.get(f"https://api.gbif.org/v1/species/{especie['name']}", timeout=60).json()
        especie["nome_cientifico"] = dados.get("canonicalName")
    print(f"   {beija_flores['total']} registros, {len(beija_flores['especies'])} espécies")
    salvar_json(beija_flores, "gbif_beija_flores.json")

    print("\nColeta concluída! Próxima etapa: 2_tratamento.py")

if __name__ == "__main__":
    main()