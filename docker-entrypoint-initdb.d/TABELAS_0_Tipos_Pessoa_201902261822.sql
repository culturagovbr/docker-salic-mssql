INSERT INTO Tabelas.dbo.Tipos_Pessoa (tpe_codigo,tpe_descricao,tpe_pf_pj,tpe_direito,tpe_fim,tpe_status) VALUES 
(0,'Não Informado',0,0,0,1)
,(1,'Pessoa Física',1,0,0,1)
,(2,'Pessoa Jurídica',2,0,0,1)
,(3,'Pessoa Jurídica de Direito Público',2,1,0,1)
,(4,'Pessoa Jurídica de Direito Privado',2,2,0,1)
,(5,'Pessoa Jurídica de Direito Privado com fins Lucrativos',2,2,1,1)
,(6,'Pessoa Jurídica de Direito Privado sem fins Lucrativos',2,2,2,1)
,(7,'Órgãos Internos da Administração Pública',3,3,3,1)
;