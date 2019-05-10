CREATE TRIGGER trPreProjeto_Insert
       ON sac.dbo.PreProjeto
       FOR INSERT
AS

DECLARE @idProjeto int
DECLARE @idUsuario int
DECLARE @idAgente  int
DECLARE @Erro      int
DECLARE @Rows      int

BEGIN TRAN
-- ====================================================================================
-- PEGAR O idProjeto e o idUsuario
-- ====================================================================================
SELECT @idProjeto = idPreProjeto,@idAgente = idAgente, @idUsuario = idUsuario FROM INSERTED
-- ====================================================================================
IF (NOT EXISTS(SELECT * FROM Agentes.dbo.Agentes WHERE idAgente = @idAgente) OR
    @idAgente = 0)
   BEGIN
     RAISERROR('1. Proponente inexistente. , transação cancelada.',16,1,@Erro)
     ROLLBACK TRAN
     RETURN
   END
-- ====================================================================================
-- INCLUIR DADOS NA TABELA MOVIMENTACAO
-- ====================================================================================
IF NOT EXISTS (SELECT * FROM tbMovimentacao WHERE idProjeto = @IdProjeto)
   BEGIN
     INSERT INTO tbMovimentacao
                (idProjeto,Movimentacao,DtMovimentacao,stEstado,Usuario)
         VALUES (@idProjeto,95,getdate(),0,@idUsuario)
   END

SELECT @Rows = @@ROWCOUNT, @Erro = @@ERROR

IF @Erro <> 0
   BEGIN
     RAISERROR('2. Erro ao tentar inserir a movimentação , transação cancelada.',16,1,@Erro)
     ROLLBACK TRAN
     RETURN
   END

IF @Rows > 1
   BEGIN
     RAISERROR('3. Erro ao tentar inserir mais de um registro (%d) na tabela movimentação , transação cancelada.',16,1,@Rows)
     ROLLBACK TRAN
     RETURN
   END

COMMIT TRAN;
