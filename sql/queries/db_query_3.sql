USE spotify_db;
-- ==================================
-- 			Consulta nº 3
-- ==================================
-- Consulta Secundária, Retorna as 5 músicas mais populares do artista
-- **********************************
SELECT ART.nome AS artista,
	MS.nome AS musica,
    MS.popularidade AS popularidade
FROM musica AS MS
JOIN participacao AS PT ON MS.id_track = PT.FK_MUSICA_id_track
JOIN artista AS ART ON PT.FK_ARTISTA_id_artista = ART.id_artista
WHERE ART.nome LIKE "%%"
ORDER BY MS.popularidade DESC
LIMIT 5
;