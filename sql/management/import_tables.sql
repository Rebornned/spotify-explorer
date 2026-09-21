/*
=========================================================
  Importacao dos CSVs gerados por scripts/generate_csv_tables.py
=========================================================

  A ordem abaixo respeita a dependencia das chaves estrangeiras.
  Alterar a ordem causa erro de integridade referencial.

  Antes de executar:

  1. Substitua CAMINHO_DO_REPOSITORIO pelo caminho absoluto da sua
     copia local do projeto. Use barras normais (/) mesmo no Windows.
     Exemplo: C:/Users/seu_usuario/PF-2026.1-BD-Spotify

  2. LOAD DATA LOCAL INFILE exige que o recurso esteja habilitado
     nos dois lados da conexao:
       - no servidor:  SET GLOBAL local_infile = 1;
       - no cliente:   mysql --local-infile=1 -u usuario -p

  3. LINES TERMINATED BY depende de como os CSVs foram gerados.
     Os arquivos versionados em /scripts_output usam CRLF (\r\n).
     Se voce regerou os CSVs em Linux ou macOS, troque para '\n'.

  Alternativa mais simples: importar o dump pronto em
  /database/spotify_db_export.sql, que ja contem esquema e dados.
=========================================================
*/

USE spotify_db;

-- 1. GENERO -----------------------------------------------------
LOAD DATA LOCAL INFILE 'CAMINHO_DO_REPOSITORIO/scripts_output/genero.csv'
INTO TABLE GENERO
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(id_genero, nome);

-- 2. ALBUM ------------------------------------------------------
LOAD DATA LOCAL INFILE 'CAMINHO_DO_REPOSITORIO/scripts_output/album.csv'
INTO TABLE ALBUM
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(id_album, nome);

-- 3. ARTISTA ----------------------------------------------------
LOAD DATA LOCAL INFILE 'CAMINHO_DO_REPOSITORIO/scripts_output/artista.csv'
INTO TABLE ARTISTA
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(id_artista, nome);

-- 4. MUSICA -----------------------------------------------------
LOAD DATA LOCAL INFILE 'CAMINHO_DO_REPOSITORIO/scripts_output/musica.csv'
INTO TABLE MUSICA
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(id_track, nome, popularidade, tempo_ms,
 FK_GENERO_id_genero, FK_ALBUM_id_album);

-- 5. PARTICIPACAO -----------------------------------------------
LOAD DATA LOCAL INFILE 'CAMINHO_DO_REPOSITORIO/scripts_output/participacao.csv'
INTO TABLE PARTICIPACAO
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(FK_MUSICA_id_track, FK_ARTISTA_id_artista, tipo_participacao);

-- Validacao -----------------------------------------------------
SELECT 'GENERO' AS tabela, COUNT(*) AS registros FROM GENERO
UNION ALL SELECT 'ALBUM', COUNT(*) FROM ALBUM
UNION ALL SELECT 'ARTISTA', COUNT(*) FROM ARTISTA
UNION ALL SELECT 'MUSICA', COUNT(*) FROM MUSICA
UNION ALL SELECT 'PARTICIPACAO', COUNT(*) FROM PARTICIPACAO;
