INSERT INTO ControleDeAcesso.dbo.SGCacesso (Cpf,Nome,DtNascimento,Email,Senha,DtCadastro,Situacao,DtSituacao) VALUES 
('23969156149','Admin','1988-04-17 00:00:00.000','salicweb@gmail.com','&nH4<!VzM(hP~n`','2019-05-10 00:00:00.000',1,'2019-05-10 00:00:00.000')
;
INSERT INTO tabelas.dbo.usuarios (usu_codigo,usu_identificacao,usu_nome,usu_pessoa,usu_orgao,usu_sala,usu_ramal,usu_nivel,usu_exibicao,usu_SQL_login,usu_SQL_senha,usu_duracao_senha,usu_data_validade,usu_limite_utilizacao,usu_senha,usu_validacao,usu_status,usu_seguranca,usu_data_atualizacao,usu_conta_nt,usu_dica_intranet,usu_controle,usu_localizacao,usu_andar,usu_telefone) VALUES 
(236,'23969156149','Admin',536,251,'0',0,9,'S','23969156149','B',30,'2018-12-17 12:16:00.000','2019-07-30 00:00:00.000','&nH4<!VzM(hP~n`','E(*2o"P],c',1,'$O\=?})0','2017-11-27 17:25:00.000',-1,10014,NULL,1,'1','2024-2368 ')
;

-- Agente Proponente
INSERT INTO Agentes.dbo.Agentes (CNPJCPF, CNPJCPFSuperior, TipoPessoa, DtCadastro, DtAtualizacao, DtValidade, Status, Usuario) VALUES('23969156149', '00000000000000', 0, '2009-01-24 10:31:33.910', '2011-10-25 11:39:11.710', '2012-10-24 11:39:11.710', 0, 236);
INSERT INTO Agentes.dbo.Nomes (idAgente, TipoNome, Descricao, Status, Usuario) VALUES(1, 18, 'Admin', 0, 236);
INSERT INTO Agentes.dbo.EnderecoNacional (idAgente, TipoEndereco, TipoLogradouro, Logradouro, Numero, Bairro, Complemento, Cidade, UF, Cep, Municipio, UfDescricao, Status, Divulgar, Usuario) VALUES(1, 23, 44, 'QR 404 Conjunto 19', '14', 'Samambaia Norte (Samambaia)', '', '530010', 53, '72318121', NULL, NULL, 0, 0, 236);
INSERT INTO Agentes.dbo.Telefones (idAgente, TipoTelefone, UF, DDD, Numero, Divulgar, Usuario) VALUES(1, 25, 53, 61, '2024-2169', 0, 236);
INSERT INTO Agentes.dbo.Internet (idAgente, TipoInternet, Descricao, Status, Divulgar, Usuario) VALUES(1, 28, 'salicweb@gmail.com', 1, 0, 236);

-- Técnicos de admissibilidade SAV E SEFIC(no dump de produçao o usuario 246 nao possui esses perfis)
INSERT INTO Tabelas.dbo.UsuariosXOrgaosXGrupos (uog_usuario, uog_orgao, uog_grupo, uog_status) VALUES(236, 262, 92, 1);
INSERT INTO Tabelas.dbo.UsuariosXOrgaosXGrupos (uog_usuario, uog_orgao, uog_grupo, uog_status) VALUES(236, 166, 92, 1);

-- Componente da comissao CNIC
-- no enquadramento o codigo area do projeto deve ser o mesmo do componente da comissao 
INSERT INTO Tabelas.dbo.UsuariosXOrgaosXGrupos (uog_usuario, uog_orgao, uog_grupo, uog_status) VALUES(236, 400, 118, 1);
INSERT INTO Agentes.dbo.tbTitulacaoConselheiro (idAgente, cdArea, cdSegmento, stTitular, stConselheiro) VALUES(1, '5', '0', 1, 'A');
