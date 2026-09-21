USE spotify_db;
-- ==================================
-- 			Consulta nº 7
-- ==================================
-- Consulta Secundária, retorna a música mais popular de cada gênero
-- **********************************
SELECT
    GEN.nome AS genero,
    MS.nome AS musica,
    MS.popularidade
FROM musica MS
JOIN genero GEN
ON GEN.id_genero = MS.FK_GENERO_id_genero
JOIN (
    SELECT
        FK_GENERO_id_genero,
        MAX(popularidade) AS max_pop
    FROM musica
    GROUP BY FK_GENERO_id_genero
) ranking
    ON ranking.FK_GENERO_id_genero = MS.FK_GENERO_id_genero
   AND ranking.max_pop = MS.popularidade
ORDER BY GEN.nome
LIMIT 5
;