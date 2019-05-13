
CREATE TRIGGER trAvaliacaoProposta_Update ON dbo.tbAvaliacaoProposta
       FOR UPDATE
AS
-- ==========================================================================================
-- Autor: Rômulo Menhô Barbosa
-- Data de Criação: 29/11/2012
-- Descrição: Reditribuir proposta entre Secretarias ou alterar o tecníco de admissibilidade.
--            Somente Incentivo Fiscal Federal
-- ==========================================================================================
-- ==========================================================================================
--- DECLARAÇÃO DE VARIÁVEIS
-- ==========================================================================================
DECLARE @idProjeto           int
DECLARE @idAvaliacaoProposta int
DECLARE @Erro            int
DECLARE @Rows            int
DECLARE @idTecnico       int
DECLARE @idTecnico_Ins   int
DECLARE @idTecnico_Del   int
DECLARE @Qtde            int
DECLARE @QtdeAnt         int
DECLARE @idTecnicoAnt    int
DECLARE @Orgao_Ins       int
DECLARE @Orgao_Del       int
DECLARE @idEdital        int
-- ==========================================================================================
-- RECUPERAR INFORMAÇÕES
-- ==========================================================================================
-- RECUPERAR O IDPROJETO E DOS TÉCNICOS
SELECT @idAvaliacaoProposta = idAvaliacaoProposta,  @idProjeto = IdProjeto, @idTecnico_Ins = idTecnico FROM Inserted
SELECT @idTecnico_Del = idTecnico FROM Deleted
-- DESCOBRIR SE É INCENTIVO FISCAL OU EDITAL
SELECT @idEdital = idEdital FROM PreProjeto WHERE idPreProjeto = @idProjeto
IF @idEdital IS NULL
BEGIN
--RECUPERAR A UNIDADE DOS TÉCNICOS
SELECT @Orgao_Ins = uog_orgao FROM tabelas.dbo.vwUsuariosOrgaosGrupos 
       WHERE sis_codigo=21 and gru_codigo=92 and uog_status = 1 and usu_codigo = @idTecnico_Ins
SET  @Orgao_Ins = ISNULL(@Orgao_Ins,0)
                            
SELECT @Orgao_Del = uog_orgao FROM tabelas.dbo.vwUsuariosOrgaosGrupos 
                              WHERE sis_codigo=21 and gru_codigo=92 and uog_status = 1 and usu_codigo = @idTecnico_Del
SET  @Orgao_Del = ISNULL(@Orgao_Del,0)
 
IF @Orgao_Del = 0
   BEGIN
     SELECT @Orgao_Del = uog_orgao FROM tabelas.dbo.vwUsuariosOrgaosGrupos where usu_codigo=@idTecnico_Del AND uog_status = 0
     SET  @Orgao_Del = ISNULL(@Orgao_Del,0)
   END
--SELECT @idAvaliacaoProposta,@idTecnico_Ins AS idTecnico_Ins , @idTecnico_Del AS idTecnico_Del, @Orgao_Ins AS Orgao_Ins, @Orgao_Del AS Orgao_Del
                                    
IF @idTecnico_Ins = @idTecnico_Del
   BEGIN
      IF @Orgao_Del = 171
         SET @Orgao_Ins = 262
      ELSE
      IF @Orgao_Del = 262
         SET @Orgao_Ins = 171
   END
-- SELECT @idAvaliacaoProposta,@idTecnico_Ins AS idTecnico_Ins , @idTecnico_Del AS idTecnico_Del, @Orgao_Ins AS Orgao_Ins, @Orgao_Del AS Orgao_Del
-- ==========================================================================================
-- INCENTIVO FISCAL FEDERAL  - ALTERAÇÃO DE TÉCNICO
-- ==========================================================================================
IF @idTecnico_Ins <> @idTecnico_Del AND @Orgao_Ins = @Orgao_Del AND (@Orgao_Ins <> 0 AND @Orgao_Ins <> 0)                                                      
   BEGIN
     --SELECT 'Técnico # e Órgão = : ', @idAvaliacaoProposta
     UPDATE tbAvaliacaoProposta 
            SET idTecnico = @idTecnico_Ins 
            WHERE idProjeto = @IdProjeto AND idAvaliacaoProposta = @idAvaliacaoProposta AND stEstado = 0
     SELECT @Rows = @@ROWCOUNT, @Erro = @@ERROR
     
     IF @Erro <> 0
        BEGIN
          RAISERROR('1. Erro ao ALTERAR registros %d na tabela tbAvaliacaoProposta, transação cancelada.',16,1,@Erro)
          ROLLBACK 
          RETURN
        END
     
     IF @Rows > 1
        BEGIN
          RAISERROR('2. Não é permitido ALTERAR %d registros ao mesmo tempo na tabela tbAvaliacaoProposta, transação cancelada',16,1,@Rows)
          ROLLBACK 
          RETURN
        END
   END     
-- ==========================================================================================
-- INCENTIVO FISCAL FEDERAL  - ALTERAÇÃO DE TÉCNICO
-- ==========================================================================================
ELSE
--IF @idTecnico_Ins = @idTecnico_Del  AND @Orgao_Ins <> @Orgao_Del AND (@Orgao_Ins <> 0 AND @Orgao_Ins <> 0) 
   BEGIN   
     --SELECT 'Técnico = e Órgão # : ', @idAvaliacaoProposta
     SET @QtdeAnt = 9999
     --==================================================================================================
     -- INCENTIVO FISCAL FEDERAL - SELECIONAR O TÉNCICO DA NOVA UNIDADE
     --==================================================================================================
     DECLARE TheCursor CURSOR FOR
       SELECT usu_codigo,uog_orgao FROM tabelas.dbo.vwUsuariosOrgaosGrupos 
              WHERE sis_codigo=21 and gru_codigo=92 and uog_orgao = @Orgao_Ins and uog_status = 1
       
     OPEN TheCursor        
     WHILE @@FETCH_STATUS = @@FETCH_STATUS
       BEGIN
         FETCH NEXT FROM TheCursor into @idTecnico,@Orgao_Ins          
         IF @@FETCH_STATUS = -2
            CONTINUE
         IF @@FETCH_STATUS = -1
            BREAK
                                
         SELECT @Qtde=count(*) FROM tbAvaliacaoProposta a
                INNER JOIN tabelas.dbo.vwUsuariosOrgaosGrupos  u ON (a.idTecnico = u.usu_Codigo)
                WHERE uog_orgao = @Orgao_Ins AND idTecnico = @idTecnico and sis_codigo = 21 and gru_codigo = 92 and 
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
     --==================================================================================================
     -- INCENTIVO FISCAL FEDERAL - ATUALIZAR O TÉNCICO DA NOVA UNIDADE
     --==================================================================================================
     UPDATE tbAvaliacaoProposta 
            SET idTecnico = @idTecnicoAnt 
            WHERE idProjeto = @IdProjeto AND idAvaliacaoProposta = @idAvaliacaoProposta AND stEstado = 0
     SELECT @Rows = @@ROWCOUNT, @Erro = @@ERROR
     
     IF @Erro <> 0
        BEGIN
          RAISERROR('1. Erro ao ALTERAR registros %d na tabela tbAvaliacaoProposta, transação cancelada.',16,1,@Erro)
          ROLLBACK 
          RETURN
        END
     
     IF @Rows > 1
        BEGIN
          RAISERROR('2. Não é permitido ALTERAR %d registros ao mesmo tempo na tabela tbAvaliacaoProposta, transação cancelada',16,1,@Rows)
          ROLLBACK 
          RETURN
        END     
   END
END

