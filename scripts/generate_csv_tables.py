import pandas as pd
import csv 

df = pd.read_csv("../dataset/spotify_tracks.csv")

# remover indice antigo
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

print("Linhas originais:", len(df))

# remover nulos importantes

df = df.dropna(
    subset=[
        'track_id',
        'artists',
        'album_name',
        'track_name'
    ]
)

print("Após remover nulos:", len(df))

# remover músicas duplicadas

df = df.drop_duplicates(
    subset=['track_id']
)

print("Após remover duplicatas:", len(df))

print()

print(df.head())

# ==========================
# GERAR TABELA GENERO
# ==========================

genero = (
    df[['track_genre']]
    .drop_duplicates()
    .reset_index(drop=True)
)

genero['id_genero'] = genero.index + 1

genero = genero.rename(
    columns={
        'track_genre':'nome'
    }
)

# reorganizar ordem

genero = genero[
    ['id_genero','nome']
]

print()

print("Quantidade generos:")

print(len(genero))

print()

print(genero.head(10))

# =====================================
# GERAR TABELA ALBUM
# =====================================

album = (
    df[['album_name']]
    .drop_duplicates()
    .reset_index(drop=True)
)

album['id_album'] = album.index + 1

album = album.rename(
    columns={
        'album_name':'nome'
    }
)

album = album[
    ['id_album','nome']
]

print("\nQuantidade albuns:")

print(len(album))

print(album.head())


# =====================================
# GERAR TABELA ARTISTA
# =====================================

todos_artistas = []

for artistas in df['artists']:

    nomes = str(artistas).split(";")

    for nome in nomes:

        nome = nome.strip()

        if nome:

            todos_artistas.append(nome)

artista = pd.DataFrame(
    {'nome':todos_artistas}
)

artista = artista.drop_duplicates()

artista = artista.reset_index(
    drop=True
)

artista['id_artista'] = (
    artista.index + 1
)

artista = artista[
    ['id_artista','nome']
]

print("\nQuantidade artistas:")

print(len(artista))

print(artista.head())


# =====================================
# MAPAS AUXILIARES
# =====================================

map_genero = dict(
    zip(
        genero['nome'],
        genero['id_genero']
    )
)

map_album = dict(
    zip(
        album['nome'],
        album['id_album']
    )
)

map_artista = dict(
    zip(
        artista['nome'],
        artista['id_artista']
    )
)


# =====================================
# GERAR TABELA MUSICA
# =====================================

musica = pd.DataFrame()

musica['id_track'] = df['track_id']

musica['nome'] = df['track_name']

musica['popularidade'] = df['popularity']

musica['tempo_ms'] = df['duration_ms']

musica['FK_GENERO_id_genero'] = (
    df['track_genre']
    .map(map_genero)
)

musica['FK_ALBUM_id_album'] = (
    df['album_name']
    .map(map_album)
)

print("\nQuantidade musicas:")

print(len(musica))

print(musica.head())


# =====================================
# GERAR PARTICIPACAO
# =====================================

participacoes = []

for _, row in df.iterrows():

    nomes = str(
        row['artists']
    ).split(";")

    for i, artista_nome in enumerate(nomes):

        artista_nome = artista_nome.strip()

        participacoes.append({

            'FK_MUSICA_id_track':
                row['track_id'],

            'FK_ARTISTA_id_artista':
                map_artista[
                    artista_nome
                ],

            'tipo_participacao':
                'principal'
                if i == 0
                else 'feat'
        })

participacao = pd.DataFrame(
    participacoes
)

print("\nQuantidade participacoes:")

print(len(participacao))

print(participacao.head())


# =====================================
# EXPORTAR CSVs
# =====================================

genero.to_csv(
    "../scripts_output/genero.csv",
    encoding="utf-8",
    index=False,
    quoting=1
)

album.to_csv(
    "../scripts_output/album.csv",
    encoding="utf-8",
    index=False,
    quoting=1
)

artista.to_csv(
    "../scripts_output/artista.csv",
    index=False,
    quoting=1
)

musica.to_csv(
    "../scripts_output/musica.csv",
    encoding="utf-8",
    index=False,
    quoting=1
)

participacao.to_csv(
    "../scripts_output/participacao.csv",
    encoding="utf-8",
    index=False,
    quoting=1
)

print("\nCSVs exportados com sucesso.")