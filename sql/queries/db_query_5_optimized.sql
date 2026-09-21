-- USE spotify_db;
-- ==================================
-- 			Consulta nº 5 - teste
-- ==================================
-- Consulta Secundária, Retorna as estatistícas de um álbum
-- **********************************
SELECT ALB.nome AS album,
	COUNT(DISTINCT MS.id_track) AS qtd_musicas,
    AVG(MS.popularidade) AS popularidade_media,
    COUNT(DISTINCT ART.id_artista) AS qtd_artistas
FROM participacao AS PT
JOIN (
	SELECT * FROM artista
    WHERE artista.nome LIKE "%"
) AS ART ON PT.FK_ARTISTA_id_artista = ART.id_artista
JOIN musica as MS
ON PT.FK_MUSICA_id_track = MS.id_track
JOIN album as ALB
ON MS.FK_ALBUM_id_album = ALB.id_album
GROUP BY ALB.id_album
ORDER BY qtd_musicas DESC
LIMIT 10
;