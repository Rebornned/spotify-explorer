USE spotify_db;
-- ==================================
-- 			Consulta nº 6
-- ==================================
-- Consulta Secundária, retorna Artistas com a média maior de músicas
-- **********************************
SELECT ART.nome, 
	COUNT(*) AS total_musicas
FROM artista ART
JOIN participacao PT
    ON ART.id_artista = PT.FK_ARTISTA_id_artista
GROUP BY ART.id_artista, ART.nome
HAVING COUNT(*) >
(
    SELECT AVG(qtd)
    FROM (
        SELECT COUNT(*) AS qtd
        FROM participacao
        GROUP BY FK_ARTISTA_id_artista
    ) AS media_artistas
)
ORDER BY total_musicas DESC
LIMIT 5
;