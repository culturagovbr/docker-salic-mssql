CREATE TRIGGER trMovimentacao_Insert ON dbo.tbMovimentacao
       INSTEAD OF INSERT
AS

-- ====================================================================================
-- Autor: Rômulo Menhô Barbosa
-- Data de Criação: 02/10/2008
-- Descrição: Movimenta a proposta e ou projeto e distribui ao analista.
-- Data de alteração: 28/10/2009
-- Motivo: Inclusão do contador mensal de quantidade de proposta por técnico.
-- Data de alteração: 15/07/2011
-- Motivo: Alterar o balanceamento para editais (140 - Tecnico de Admissibilidade de Edital)
-- Data de alteração: 21/07/2011
-- Motivo: Corrigir o balanceamento para editais (92 - Tecnico de Admissibilidade)
-- ====================================================================================

  
DECLARE @idMovimentacao int
DECLARE @idProjeto      int
DECLARE @Movimentacao   int
DECLARE @DtMovimentacao datetime
DECLARE @Status         bit
DECLARE @Usuario        int
DECLARE @Rows           int
DECLARE @idTecnico      int
DECLARE @Qtde           int
DECLARE @QtdeAnt        int
DECLARE @idTecnicoAnt   int
DECLARE @Orgao          int
DECLARE @OrgaoSuperior  int
DECLARE @AreaAbrangencia int
DECLARE @idEdital          int

SET @idEdital = null

SELECT @idMovimentacao=idMovimentacao,@idProjeto=idProjeto,@Movimentacao=Movimentacao,
       @DtMovimentacao=DtMovimentacao,@Status=stEstado,@Usuario=Usuario 
       FROM Inserted

SELECT @idEdital = idEdital FROM dbo.PreProjeto WHERE idPreProjeto = @idProjeto

-- Inserir dados na tabela de movimentação
IF EXISTS (SELECT * FROM tbMovimentacao WHERE idProjeto = @IdProjeto)                                                             
   BEGIN
     UPDATE tbMovimentacao
        SET stEstado = 1
     WHERE idProjeto = @IdProjeto AND stEstado = 0
   END

INSERT INTO tbMovimentacao
           (idProjeto,Movimentacao,DtMovimentacao,stEstado,Usuario)
    VALUES (@IdProjeto,@Movimentacao,@DtMovimentacao,0,@Usuario)         

-- Distribuir proposta entre os avaliadores da SEFIC/SAV
IF NOT EXISTS(SELECT * FROM tbAvaliacaoProposta WHERE idProjeto = @IdProjeto)
   BEGIN
     SET @QtdeAnt = 9999
     --==================================================================================================
     -- INCENTIVO FISCAL FEDERAL
     --==================================================================================================
     IF @idEdital IS NULL
        BEGIN
             SELECT @AreaAbrangencia = AreaAbrangencia FROM PreProjeto WHERE idPreProjeto = @IdProjeto
             IF @AreaAbrangencia = 0
                BEGIN 
                  SET @OrgaoSuperior = 251
                END
             ELSE
                BEGIN 
                    SET @OrgaoSuperior = 160
                     END
             DECLARE TheCursor CURSOR FOR
                SELECT usu_codigo,uog_orgao FROM tabelas.dbo.vwUsuariosOrgaosGrupos 
                  WHERE sis_codigo=21 and gru_codigo=92 and org_superior = @OrgaoSuperior and uog_status = 1
        END
     ELSE
     --==================================================================================================
     -- EDITAL
     --==================================================================================================
        BEGIN
          SELECT @OrgaoSuperior = idOrgao FROM dbo.Edital WHERE idEdital = @idEdital
               
          DECLARE TheCursor CURSOR FOR
             SELECT usu_codigo,uog_orgao FROM tabelas.dbo.vwUsuariosOrgaosGrupos 
                WHERE sis_codigo=21 and gru_codigo=140 and uog_orgao = @OrgaoSuperior and uog_status = 1
        END
       
     OPEN TheCursor        
     WHILE @@FETCH_STATUS = @@FETCH_STATUS
       BEGIN
         FETCH NEXT FROM TheCursor into @idTecnico,@Orgao          
         IF @@FETCH_STATUS = -2
            CONTINUE
         IF @@FETCH_STATUS = -1
            BREAK
                                
         SELECT @Qtde=count(*) FROM tbAvaliacaoProposta a
               INNER JOIN tabelas.dbo.vwUsuariosOrgaosGrupos  u ON (a.idTecnico = u.usu_Codigo)
        WHERE uog_orgao=@Orgao AND idTecnico=@idTecnico and sis_codigo=21 and gru_codigo in (92,140) and 
                     stEstado = 0 and year(DtAvaliacao)=year(Getdate()) and month(DtAvaliacao)=month(Getdate())

         SET @Qtde = ISNULL(@Qtde,0)
         IF @QtdeAnt > @Qtde 
            BEGIN
              SET @QtdeAnt      = @Qtde
              SET @idTecnicoAnt = @idTecnico
            END
       END            
     CLOSE TheCursor
     DEALLOCATE TheCursor
     
     IF @Movimentacao = 96 AND @Status = 0
        BEGIN
          INSERT INTO tbAvaliacaoProposta
                     (idProjeto,idTecnico,DtEnvio,ConformidadeOK)
              VALUES (@idProjeto,@idTecnicoAnt,@DtMovimentacao,9)
        END         
   END;
