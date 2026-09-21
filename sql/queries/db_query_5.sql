USE spotify_db;
-- ==================================
-- 			Consulta nº 5
-- ==================================
-- Consulta Secundária, Retorna as estatistícas de um álbum
-- **********************************
SELECT ALB.nome AS album,
	COUNT(DISTINCT MS.id_track) AS qtd_musicas,
    AVG(MS.popularidade) AS popularidade_media,
    COUNT(DISTINCT ART.id_artista) AS qtd_artistas
FROM album AS ALB
LEFT JOIN musica AS MS ON ALB.id_album = MS.FK_ALBUM_id_album
LEFT JOIN participacao AS PT ON MS.id_track = PT.FK_MUSICA_id_track
LEFT JOIN artista AS ART ON PT.FK_ARTISTA_id_artista = ART.id_artista
GROUP BY ALB.id_album
HAVING ALB.nome LIKE "%%"
ORDER BY qtd_musicas DESC
LIMIT 5
;