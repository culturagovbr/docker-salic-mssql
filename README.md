# docker-salic-mssql
Docker para rodar o banco do Salic para desenvolvimento(SQL Server) e ferramenta de importação de dados.

## MacOS
Atualmente existe alguns problemas para compartilhamento de volume e mapeamentos de portas nessa imagem para o MacOS o comando abaixo resolve.
```
docker-compose run --rm --service-ports salic-mssql
```
## Linux
Ajustar o docke-compose.yml para linux

Fazer o build para gerar as tabelas
```
docker-compose up --build
```

Sem gerar tabelas
```
docker-compose up
```

work in progress 

# Migrações

Este container conta com uma ferramenta de migração, que permite que dados sejam migrados de um banco para outro. Isso vale para qualquer banco com inserção autorizada por credenciais. É possível escolher uma fonte de dados num banco de produção, desenvolvimento, homologação etc, e definir um banco alvo - um docker ou mesmo um banco de hmg/dev.

## Configurando origem e destino:

Para configurar os bancos de dados, preencha os dados para db_source (origem) e db_target (destino) no arquivo **migrate/dbconfig.py**:

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

db_config = {
    "db_source": {
        "host": "otherhost",
        "user": "user",
        "pass": "password",
        "port": "1434",
        "dbname": "sac",
        "schema": "dbo",
    },
    "db_target": {
        "host": "localhost",
        "user": "SA",
        "pass": "salic@123456",
        "port": "1433",
        "dbname": "sac",
        "schema": "dbo",
    }
}
```

## Funcionalidades

Atualmente, a ferramenta de importação possui duas funcionalidades: migrate e flush

### Migrate

Executa a importação de dados a partir de um **db_source** para um **db_target**.

### Flush

Apaga todos os dados das tabelas especificadas para um **db_target**.

## Importando dados específicos do seu módulo

Ao fazer o build do docker-compose, uma primeira migração será executada. Ela contém diversas tabelas de apoio e usuários padrão para realizar login.

Para gerar uma migração com os dados do seu módulo (ex: parecer, readequação, comprovação financeira etc) é necessário criar os arquivos de tabelas com as respectivas condições de importação, na pasta migrate/tables/[nomedomodulo].

Cada pasta de módulo contém arquivos de definição de tabelas, separadas por arquivos com o padrão **'[00]-[nomedobanco].[schema].tbl'**. No caso, 00 seria a ordem de execução, nomedobanco o nome do database, e schema. Os arquivos devem possuir a terminação .tbl e obedecer o padrão descrito; caso contrário, não serão executados. Exemplos válidos para o salic de definições de bancos válidas:

```
$ ls migrate/tables/0-initial
00-agentes.dbo.tbl
01-sac.dbo.tbl
02-tabelas.dbo.tbl
```

Dentro dos arquivos de definição de tabelas, o padrão é o abaixo:
```
[nome_da_tabela]|[CONDIÇÕES]|[chave_primária]
```

Num caso real, seria:

```
tipos_pessoa||
categorias_pessoa||
pessoas|INNER JOIN tabelas.dbo.Usuarios on usuarios.usu_pessoa = pessoas.pes_codigo and usuarios.usu_identificacao = '12345678900'|
pessoa_identificacoes|INNER JOIN tabelas.dbo.orgaos on orgaos.org_pessoa = pessoa_identificacoes.pid_pessoa|pid_pessoa
```

Toda tabela que precisar de JOINs ou de restrições WHERE deve ter esse tipo de dado preenchido na segunda posição entre | (pipes). Caso esse campo estiver vazio, o SQL executado será um *SELECT * FROM* sem restrições. O mesmo vale para chave primária: caso não seja especificada, o script buscará pela primeira chave primária informada no banco.

Outro detalhe importante é a ordem de execução: primeiro as tabelas assistentes, ou com dados que servirão a relacionamentos (constraints). No caso de um FLUSH, a ordem de execução é invertida - isto é, são executadas as instruções de baixo primeiro. No FLUSH até o momento não existe a opção de exclusão condicional de uma tabela, o que quer dizer que todos os dados daquela tabela serão apagados.


## Uso 

```
$ docker exec -it salic-mssql bash
# cd migrate
# ./main migrate nomedomodulo

# ./main flush nomedomodulo
```
