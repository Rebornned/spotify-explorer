# ===================================================
#                   Imports
# ===================================================
from flask import Blueprint, render_template, session
from sqlalchemy import text
from . import db
from .queries import *
from .models import Musica, Album, Genero, Artista, Participacao
from flask import jsonify, request
# ===================================================
#           Global variables for routes
# ===================================================
main = Blueprint("main", __name__)

# ===================================================
#                       Routes
# ===================================================
# ***************************************************
#                     Main route
# ***************************************************
@main.route("/")
def index():
    return render_template(
        "index.html",
    )

@main.route('/api/teste-spotify')
def teste_spotify():
    # Teste de conexão entre o Node e o Flask, e também com o banco de dados
    s_value = ""
    query = db.session.execute(
    text(
        main_query(
        order_type="ms_popularity", 
        search_type="ms_name", 
        offset=0,
        limit=1,
        order_mode="DESC"
        )),
        {
        "search_value": f"%{s_value}%"
        }
    )
    result = query.mappings().all()
    return jsonify([dict(row) for row in result])
# ***************************************************
#                     Music route
# ***************************************************
@main.route('/api/musicas')
def listar_musicas():
    # 1. Captura os parâmetros enviados pelo React
    busca = request.args.get('busca', '')
    campo_busca = request.args.get('campoBusca', 'musica')  
    ordem_front = request.args.get('ordem', 'popularidade') 
    direcao = 'ASC' if request.args.get('direcao', 'desc').lower() == 'asc' else 'DESC'
    pagina = max(1, int(request.args.get('pagina', 1) or 1))
    
    limit = 10
    offset = (pagina - 1) * limit

    # 2. Mapeia o campo de busca vindo do front
    mapa_busca = {
        "musica": "ms_name",
        "artista": "art_name",
        "album": "alb_name",
        "genero": "gen_name"
    }
    search_type = mapa_busca.get(campo_busca, "ms_name")

    # 3. Mapeia a ordenação vinda do front
    mapa_ordem = {
        "musica": "ms_name",
        "popularidade": "ms_popularity",
        "duracao": "ms_duration",
        "artista": "art_name",
        "album": "alb_name",
        "genero": "gen_name"
    }
    order_type = mapa_ordem.get(ordem_front, "ms_popularity")

    # 4. Executa a main_query (Dados da página atual)
    query_dados = text(main_query(
        order_type=order_type,
        search_type=search_type,
        offset=offset,
        limit=limit,
        order_mode=direcao
    ))
    
    search_param = f"{busca}%"
    result = db.session.execute(query_dados, {"search_value": search_param}).mappings().all()

    if search_type == "ms_name":
        sql_count = text("SELECT COUNT(*) FROM musica WHERE nome LIKE :search_value")
        
    elif search_type == "alb_name":
        sql_count = text("""
            SELECT COUNT(*) 
            FROM musica as MS
            JOIN album AS ALB ON MS.FK_ALBUM_id_album = ALB.id_album
            WHERE ALB.nome LIKE :search_value
        """)
        
    elif search_type == "gen_name":
        sql_count = text("""
            SELECT COUNT(*) 
            FROM musica as MS
            JOIN genero AS GEN ON GEN.id_genero = MS.FK_GENERO_id_genero
            WHERE GEN.nome LIKE :search_value
        """)
        
    elif search_type == "art_name":
        # Junta apenas o necessário para alcançar o artista e garante contagem única de músicas
        sql_count = text("""
            SELECT COUNT(DISTINCT MS.id_track) 
            FROM musica as MS
            JOIN participacao as PT ON MS.id_track = PT.FK_MUSICA_id_track
            JOIN artista as ART ON ART.id_artista = PT.FK_ARTISTA_id_artista
            WHERE ART.nome LIKE :search_value
        """)
    else:
        sql_count = text("SELECT COUNT(*) FROM musica")

    total_registros = db.session.execute(sql_count, {"search_value": search_param}).scalar()

    # Devolve a estrutura para o React
    return jsonify({
        "musicas": [dict(row) for row in result],
        "total": total_registros
    })

# ***************************************************
#                     Artist route
# ***************************************************
@main.route('/api/artistas')
def listar_artistas():
    busca = request.args.get('busca', '')
    pagina = max(1, int(request.args.get('pagina', 1) or 1))
    limit = 10
    offset = (pagina - 1) * limit

    query_dados = text(art_query(
        order_type="avg_popularity",
        offset=offset,
        limit=limit,
        order_mode="DESC"
    ))
    
    result = db.session.execute(query_dados, {"search_value": f"{busca}%"}).mappings().all()

    # Query de COUNT para a paginação
    sql_count = text("""
        SELECT COUNT(DISTINCT ART.id_artista)
        FROM artista AS ART
        WHERE ART.nome LIKE :search_value
    """)
    total_registros = db.session.execute(sql_count, {"search_value": f"{busca}%"}).scalar()

    return jsonify({
        "artistas": [dict(row) for row in result],
        "total": total_registros
    })

@main.route('/api/artistas/detalhes')
def detalhes_artista():
    nome_artista = request.args.get('nome', '')

    query_musicas = text(pop_msc_art_query(offset=0, limit=5))
    res_musicas = db.session.execute(query_musicas, {"search_value": f"{nome_artista}%"}).mappings().all()

    query_albuns = text(album_query(order_type="avg_popularity", offset=0, limit=3, order_mode="DESC"))
    res_albuns = db.session.execute(query_albuns, {"search_value": f"{nome_artista}%"}).mappings().all()

    return jsonify({
        "topMusicas": [dict(row) for row in res_musicas],
        "topAlbuns": [dict(row) for row in res_albuns]
    })


# ***************************************************
#                   Gender route
# ***************************************************
@main.route('/api/generos')
def listar_generos():
    busca = request.args.get('busca', '').strip()
    ordem_front = request.args.get('ordem', 'qtdMusicas')
    direcao = 'ASC' if request.args.get('direcao', 'desc').lower() == 'asc' else 'DESC'
    pagina = max(1, int(request.args.get('pagina', 1) or 1))
    
    limit = 10
    offset = (pagina - 1) * limit

    mapa_ordem = {
        "genero": "gen_name",
        "qtdMusicas": "nbo_musics",
        "popMedia": "avg_popularity",
        "qtdArtistas": "nbo_artists"
    }
    order_type = mapa_ordem.get(ordem_front, "nbo_musics")

    query_dados = text(gen_query(
        order_type=order_type,
        offset=offset,
        limit=limit,
        order_mode=direcao
    ))
    
    result = db.session.execute(query_dados, {"search_value": f"{busca}%"}).mappings().all()

    lista_generos = []
    for row in result:
        dados_row = dict(row)
        if dados_row.get('pop_media') is not None:
            dados_row['pop_media'] = round(float(dados_row['pop_media']), 1)
        else:
            dados_row['pop_media'] = 0.0
        lista_generos.append(dados_row)

    sql_count = text("""
        SELECT COUNT(DISTINCT GEN.id_genero)
        FROM genero AS GEN
        WHERE GEN.nome LIKE :search_value
    """)
    total_registros = db.session.execute(sql_count, {"search_value": f"{busca}%"}).scalar()

    return jsonify({
        "generos": lista_generos,
        "total": total_registros
    })


# ***************************************************
#                   Statistics route
# ***************************************************
@main.route('/api/estatisticas')
def obter_estatisticas():
    tipo = request.args.get('tipo', 'top10Artistas')
    lista_resultado = []

    # 1. TOP 10 ARTISTAS
    if tipo == 'top10Artistas':
        query = text(art_query(order_type="avg_popularity", offset=0, limit=10, order_mode="DESC"))
        result = db.session.execute(query, {"search_value": "%%"}).mappings().all()
        for i, row in enumerate(result):
            lista_resultado.append({
                "id": i + 1,
                "rank": i + 1,
                "artista": row["artista"],
                "qtdMusicas": row["qtd_musicas"],
                "qtdAlbuns": row["qtd_album"],
                "popMedia": round(float(row["pop_media"]), 1) if row["pop_media"] else 0.0
            })

    # 2. TOP 10 GÊNEROS
    elif tipo == 'top10Generos':
        query = text(gen_query(order_type="avg_popularity", offset=0, limit=10, order_mode="DESC"))
        result = db.session.execute(query, {"search_value": "%%"}).mappings().all()
        for i, row in enumerate(result):
            lista_resultado.append({
                "id": i + 1,
                "rank": i + 1,
                "genero": row["genero"],
                "qtdMusicas": row["qtd_musicas"],
                "popMedia": round(float(row["pop_media"]), 1) if row["pop_media"] else 0.0,
                "qtdArtistas": row["qtd_artistas"]
            })

    # 3. ARTISTAS ACIMA DA MÉDIA
    elif tipo == 'acimaMedia':
        query = text(art_avg_msc_query(offset=0, limit=5))
        result = db.session.execute(query).mappings().all()
        for i, row in enumerate(result):
            lista_resultado.append({
                "id": i + 1,
                "rank": i + 1,
                "artista": row["nome"],
                "totalMusicas": row["total_musicas"]
            })

    # 4. MÚSICA TOP POR GÊNERO
    elif tipo == 'topPorGenero':
        query = text(top_gen_msc_query(offset=0, limit=10)) 
        result = db.session.execute(query).mappings().all()
        for i, row in enumerate(result):
            lista_resultado.append({
                "id": i + 1,
                "rank": i + 1,
                "genero": row["genero"],
                "musica": row["musica"],
                "popularidade": int(row["popularidade"]) if row["popularidade"] else 0
            })

    # 5. ÁLBUNS COM MAIS MÚSICAS
    elif tipo == 'maisMusicas':
        query = text(album_query(order_type="nbo_musics", offset=0, limit=10, order_mode="DESC"))
        result = db.session.execute(query, {"search_value": "%%"}).mappings().all()
        for i, row in enumerate(result):
            lista_resultado.append({
                "id": i + 1,
                "rank": i + 1,
                "album": row["album"],
                "qtdMusicas": row["qtd_musicas"],
                "popMedia": round(float(row["pop_media"]), 1) if row["pop_media"] else 0.0
            })

    return jsonify(lista_resultado)
