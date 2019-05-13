CREATE TRIGGER HISTORICO_INSERT ON dbo.Projetos
	FOR UPDATE
AS
-- =====================================================================================================
-- Autor: Rômulo Menhô Barbosa
-- Data de Criação: 16/04/1996
-- Descrição: Controlar a alterção de situacao
-- Data de Alteração :14/10/2010.
-- Motivo: Excluir CTQE e retirada da funcionalidade de geração de historico de Unidade de Análise
-- Data de Alteração :30/10/2012.
-- Motivo: Retirada da funcionalidade de geração de historico de Unidade de Análise e
--         acertar a gravação do historico quando alterar apenas a providência tomada.
-- Data de Alteração: 30/10/2013
-- Motivo: Desativar a verificação para as Situações E10 e E12.
-- ======================================================================================================
  DECLARE @Situacao       char(3)
  DECLARE @SituacaoD      char(3)
  DECLARE @Valor          money
  DECLARE @AreaAtuacao    char(1)
  DECLARE @StatusSituacao tinyint
  DECLARE @Rows           int
  DECLARE @PessoaS        int  

  IF UPDATE (SITUACAO)
     BEGIN 
       -- ========================================================================================================
       -- Verificar a captação do projeto  
       -- ========================================================================================================
       SELECT @Valor = sum(CaptacaoReal)
              FROM Captacao c
              INNER JOIN Inserted i on (c.AnoProjeto = i.AnoProjeto and
                                        c.Sequencial = i.Sequencial)
              WHERE c.AnoProjeto = i.AnoProjeto and c.Sequencial = i.Sequencial

       SET @Valor = ISNULL(@Valor,0)
            
      -- ========================================================================================================
       -- Recuperar os Status da Situação e a Situacao
       -- ========================================================================================================
       SELECT @StatusSituacao = StatusProjeto,@Situacao = i.Situacao 
              FROM Inserted i
              INNER JOIN Situacao s on (s.Codigo = i.Situacao) 
              WHERE Codigo = i.Situacao
    
      -- ========================================================================================================
       -- Verificar a situação de arquivamento
       -- ========================================================================================================
       IF @Situacao = 'E04' AND @Valor = 0         
          BEGIN
            RAISERROR('Projeto sem captação de recursos não pode ser arquivado nesta situação. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE       
       -- ========================================================================================================
       -- Verificar o lançamento da situação E10 
       -- ========================================================================================================
     /*  IF @Situacao = 'E10' AND @Valor > 0         
          BEGIN
            RAISERROR('Situação incorreta. Para o projeto com captação a correta é E12. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE */
       -- ========================================================================================================
       -- Verificar o lançamento da situação E11 
       -- ========================================================================================================
       IF @Situacao = 'E11' AND @Valor > 0         
          BEGIN
            RAISERROR('Situação incorreta. Para o projeto com captação a correta é E15. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE
       -- ========================================================================================================
       -- Verificar o lançamento da situação E12 
       -- ========================================================================================================
      /* IF @Situacao = 'E12' AND @Valor = 0         
          BEGIN
            RAISERROR('Situação incorreta. Para o projeto sem captação a correta é E10. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE */
       -- ========================================================================================================
       -- Verificar o lançamento da situação E15 
       -- ========================================================================================================
       IF @Situacao = 'E15' AND @Valor = 0         
          BEGIN
            RAISERROR('Situação incorreta. Para o projeto sem captação a correta é E11. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE
       -- ========================================================================================================
       -- Verificar o lançamento da situação E16 
       -- ========================================================================================================
       IF @Situacao = 'E16' AND @Valor > 0         
          BEGIN
            RAISERROR('Situação incorreta.  Para o projeto com captação a correta é E23. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE
       -- ========================================================================================================
       -- Verificar o lançamento da situação E23
       -- ========================================================================================================
       IF @Situacao = 'E23' AND @Valor = 0         
          BEGIN
            RAISERROR('Situação incorreta. Para o projeto sem captação a correta é E16. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE
       -- ========================================================================================================
       -- Verificar o arquivamento do projeto
       -- ========================================================================================================
       IF @Situacao = 'K00' AND @Valor > 0         
          BEGIN
            RAISERROR('Projeto com captação de recursos não pode ser arquivado. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END   
       ELSE
       -- ========================================================================================================
       -- Situação desabilitada.
       -- ========================================================================================================
       IF @StatusSituacao = 0          
          BEGIN
            RAISERROR('Situação desabilitada. A situação do projeto não foi alterada.',16,1)
            ROLLBACK TRAN
            RETURN
          END        
       -- ========================================================================================================
       -- Gravação do Historico de Situação
       -- ========================================================================================================
       INSERT INTO HistoricoSituacao
                   (AnoProjeto,Sequencial,DtSituacao,Situacao,ProvidenciaTomada,Logon)
             SELECT d.AnoProjeto,d.Sequencial,d.DtSituacao,d.Situacao,d.ProvidenciaTomada,d.Logon
               FROM Inserted i
               INNER JOIN Deleted d ON (d.AnoProjeto = i.AnoProjeto and d.Sequencial = i.Sequencial)
               WHERE d.AnoProjeto = i.AnoProjeto and d.Sequencial = i.Sequencial and 
               (d.Situacao <> i.Situacao or d.ProvidenciaTomada <> i.ProvidenciaTomada)
     END
  ELSE   
  -- ========================================================================================================
  -- Gravação do Histórico da Providência Tomamda
  -- ========================================================================================================
  IF UPDATE (PROVIDENCIATOMADA)
     BEGIN   
       INSERT INTO HistoricoSituacao
                   (AnoProjeto,Sequencial,DtSituacao,Situacao,ProvidenciaTomada,Logon)
             SELECT d.AnoProjeto,d.Sequencial,d.DtSituacao,d.Situacao,d.ProvidenciaTomada,d.Logon
               FROM Inserted i
               INNER JOIN Deleted d ON (d.AnoProjeto = i.AnoProjeto and d.Sequencial = i.Sequencial)
               WHERE d.AnoProjeto = i.AnoProjeto and d.Sequencial = i.Sequencial and d.ProvidenciaTomada <> i.ProvidenciaTomada
             
    END

