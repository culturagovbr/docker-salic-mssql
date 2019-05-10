CREATE TRIGGER [dbo].[trPreProjeto_Delete]
       ON [dbo].[PreProjeto]
       INSTEAD OF DELETE
AS

DECLARE @Erro          int
DECLARE @Rows          int
DECLARE @idPreProjeto  int

SELECT @idPreProjeto = idPreProjeto FROM Deleted

UPDATE PreProjeto
   SET DtArquivamento=getdate(),stEstado = 0
   WHERE idPreProjeto = @idPreProjeto

   SELECT @Rows = @@ROWCOUNT, @Erro = @@ERROR

   IF @Erro <> 0
        BEGIN
          RAISERROR('1. Erro ao apagar registros %d na tabela PreProjeto transação cancelada.',16,1,@Erro)
          ROLLBACK TRAN
          RETURN
        END

    IF @Rows > 1
        BEGIN
          RAISERROR('2. Não é permitido apagar %d registros ao mesmo tempo na tabela PreProjeto, transação cancelada',16,1,@Rows)
          ROLLBACK TRAN
          RETURN
        END
