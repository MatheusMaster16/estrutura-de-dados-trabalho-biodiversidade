Como rodar o projeto

Precisa de Python e de internet.

Abra a pasta dentro do VS Code > Abra o terminal e rode os comandos abaixo, nesta ordem:

1. pip install -r requirements.txt     # 1- instala as bibliotecas
2. python 1_coleta.py                  # 2- busca os dados nas APIs do GBIF e do IBGE (leva ~2 minutos)
3. python 2_tratamento.py              # 3- limpa e organiza os dados
4. python -m streamlit run 3_dash.py   # 4- abre o dashboard no navegador


- O passo 2 cria a pasta 'dados_brutos/' (os dados como vieram das APIs);
- O passo 3 cria a pasta 'dados_tratados/' (as tabelas que o dashboard usa);
- O passo 4 abre o dashboard em 'http://localhost:8501'.

As pastas 'dados_brutos/' e 'dados_tratados/' já vêm no repositório. Para só abrir o dashboard, basta fazer os passos 1 e 4. Rodar os passos 2 e 3 busca os dados de novo nas APIs e substitui os que estão lá.

>O dashboard abre com 'python -m streamlit run 3_dash.py'. Rodar 'python 3_dash.py' (ou o botão play do VS Code) não abre a página.
