USE spotify_db;
-- ==================================
-- 			Consulta nº 1
-- ==================================
-- Consulta Principal, Retorna todas as informações.
-- **********************************
SELECT MS.nome AS Musica, 
	ART.nome AS Artista,
	ALB.nome AS Album, 
	GEN.nome AS Genero, 
    CONCAT(FLOOR(MS.tempo_ms / 60000), 'm',
        LPAD(FLOOR((MS.tempo_ms % 60000) / 1000), 2, '0'), 's') AS duracao,
	MS.popularidade AS popularidade,
    PT.tipo_participacao AS Atuacao
FROM musica as MS
JOIN album AS ALB ON MS.FK_ALBUM_id_album = ALB.id_album
JOIN participacao as PT ON MS.id_track = PT.FK_MUSICA_id_track
JOIN artista as ART ON ART.id_artista = PT.FK_ARTISTA_id_artista
JOIN genero as GEN ON GEN.id_genero = MS.FK_GENERO_id_genero
WHERE MS.nome LIKE "%%"
ORDER BY MS.tempo_ms DESC
LIMIT 5
;
