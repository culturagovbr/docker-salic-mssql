# docker-salic-mssql
Criando docker para rodar o banco do Salic para desenvolvimento(SQL Server)

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
