USE spotify_db;
-- ==================================
-- 			Consulta nº 4
-- ==================================
-- Consulta Secundária, Retorna estatísticas dos gêneros
-- **********************************
SELECT GEN.nome AS genero, 
	COUNT(DISTINCT MS.id_track) AS qtd_musicas,
    AVG(MS.popularidade) AS pop_media,
    COUNT(DISTINCT ART.id_artista) AS qtd_artistas
FROM musica AS MS 
JOIN genero AS GEN ON MS.FK_GENERO_id_genero = GEN.id_genero
JOIN participacao AS PT ON MS.id_track = PT.FK_MUSICA_id_track
JOIN artista AS ART ON PT.FK_ARTISTA_id_artista = ART.id_artista
GROUP BY GEN.id_genero
HAVING GEN.nome LIKE "%%"
ORDER BY GEN.nome ASC
LIMIT 5
;

