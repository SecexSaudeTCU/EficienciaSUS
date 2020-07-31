# EficienciaSUS
Análises de Eficiência do SUS (Sistema Único de Saúde)

<p align="justify">Este projeto foi gestacionado no Levantamento de Auditoria
que teve como objetivo conhecer o nível de eficiência relativa das unidades
hospitalares públicas de média e alta complexidade e identificar critérios para
realização de auditoria de avaliação do desempenho delas (processo do Tribunal de Contas da União: TC 015.993/2019-1).</p>

<p align="justify">As instruções de uso que se seguem servem justamente para reproduzir os passos
utilizados para computar essa eficiência relativa das unidades hospitalares públicas
de média e alta complexidade através do uso da técnica Análise Envoltória de Dados
(Data Envelopment Analysis - DEA) para dados de 2019 de três bases de dados
custodiadas pelo Datasus (Cadastro Nacional de Estabelecimentos de Saúde - CNES,
Sistema de Informações Hospilalares - SIH e Sistema de Informações Ambulatoriais - SIA):</p>

<p align="justify">1. Fazer o download
da versão <a href="https://github.com/SecexSaudeTCU/EficienciaSUS/releases/tag/0.0.1">0.0.1</a>
deste projeto que se constitui nos códigos utilizados no Levantamento de Auditoria
e coloca-lo descompactado num diretório apropriado;</p>

<p align="justify">2.1. Se não tiver Python instalado em sua máquina, instalar a
versão 3.5.4 disponível para download (Windows) em https://www.python.org/downloads/windows/.
Quando na janela do instalador selecionar a caixa de "Add Python 3.5 to PATH"; ou</p>

<p align="justify">2.2. Caso já tenha uma versão de Python instalada instalar a
versão 3.5.4 referida no passo 2.1 mas sem selecionar a caixa "Add Python 3.5 to PATH";</p>

<p align="justify">2.2.1. Instalar o pacote Python <a href="https://pypi.org/project/pipenv/">pipenv</a>;</p>

<p align="justify">2.2.2. Criar um novo projeto com pipenv no diretório raiz da
pasta descompactada baixada no passo 1 acima usando Python 3.5:</p>

```
$ pipenv --python 3.5
```

<p align="justify">2.2.3. Instalar separadamente os pacotes Python pandas,
matplotlib, scikit-learn e pyDEA (este último só funciona em Python < 3.6):</p>

```
$ pipenv install nome_do_pacote
```

<p align="justify">2.2.4. Entrar no ambiente virtual criado em Python 3.5:</p>

```
$ pipenv shell
```

<p align="justify">2.3. Mudar para o subdiretório do projeto "scripts" (Windows):</p>

```
$ cd scripts
```

<p align="justify">2.4. Executar os scripts prepara_dados.py, clusteriza.py e
executa_dea.py nessa ordem:</p>

```
$ python nome_do_script
```

<p align="justify">O Relatório deste Levantamento de Auditoria da eficiência em
unidades hospitalares públicas juntamente com seu Anexo 11, que trata especificamente
da análise DEA, podem ser baixados em XXX.</p>

<p align="justify">Conforme referido acima, a tag da versão do projeto relativa
a este Levantamento de Auditoria é a <a href="https://github.com/SecexSaudeTCU/EficienciaSUS/releases/tag/0.0.1">0.0.1</a>
onde está disponível para download. Este projeto está sendo reestruturado para
permitir, por exemplo, complementação de análises de eficiência com o uso da técnica
DEA e de outras como a Análise da Fronteira Estocástica (Stochastic Frontier Analysis - SFA).</p>
