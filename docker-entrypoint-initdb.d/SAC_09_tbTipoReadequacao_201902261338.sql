INSERT INTO SAC.dbo.tbTipoReadequacao (idTipoReadequacao,dsReadequacao,stReadequacao,stPublicacaoDou,tpAtributo,qtCaracteres,siReadequacao,stEstado) VALUES 
(1,'Remanejamento até 50 %',0,0,' ',0,1,0)
,(2,'Planilha Orçamentária',0,1,' ',0,1,0)
,(3,'Alteração de Razão Social',0,1,'T',300,0,0)
,(4,'Agência Bancária',0,0,'T',5,0,0)
,(5,'Sinópse da Obra',0,0,'C',8000,0,0)
,(6,'Impacto Ambiental',0,0,'C',8000,0,0)
,(7,'Especificação Técnica',0,0,'C',8000,0,0)
,(8,'Estratégia de Execução',0,0,'C',8000,0,0)
,(9,'Local de Realização',0,0,' ',0,1,0)
,(10,'Alteração de Proponente',0,1,'T',14,0,0)
;
INSERT INTO SAC.dbo.tbTipoReadequacao (idTipoReadequacao,dsReadequacao,stReadequacao,stPublicacaoDou,tpAtributo,qtCaracteres,siReadequacao,stEstado) VALUES 
(11,'Plano de Distribuição',0,0,' ',0,1,0)
,(12,'Nome do Projeto',0,1,'T',300,0,0)
,(13,'Período de Execução',0,0,'D',10,0,0)
,(14,'Plano de Divulgação',0,0,' ',0,0,1)
,(15,'Resumo do Projeto',0,1,'C',1000,0,0)
,(16,'Objetivos',0,0,'C',8000,0,0)
,(17,'Justificativa',0,0,'C',8000,0,0)
,(18,'Acessibilidade',0,0,'C',8000,0,0)
,(19,'Democratização de Acesso',0,0,'C',8000,0,0)
,(20,'Etapas de Trabalho',0,0,'C',8000,0,0)
;
INSERT INTO SAC.dbo.tbTipoReadequacao (idTipoReadequacao,dsReadequacao,stReadequacao,stPublicacaoDou,tpAtributo,qtCaracteres,siReadequacao,stEstado) VALUES 
(21,'Ficha Técnica',0,0,'C',8000,0,0)
,(22,'Saldo de Aplicação',0,0,'C',1000,1,0)
,(23,'Transferência de recursos entre projetos',0,0,' ',0,1,0)
;