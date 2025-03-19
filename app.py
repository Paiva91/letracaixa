from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

# Cria a instância do Flask
app = Flask(__name__)

# Configuração
USUARIO_LETTERBOXD = "wiseking"  # Substitua pelo seu usuário do Letterboxd
URL_RECENTES = f"https://letterboxd.com/{USUARIO_LETTERBOXD}/films/diary/"

# Configurações do TMDB
TMDB_API_KEY = "5c07032bfee9be2073e96d7d6af3b0cb"
TMDB_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1YzA3MDMyYmZlZTliZTIwNzNlOTZkN2Q2YWYzYjBjYiIsIm5iZiI6MTc0MjM0MjAwNi43NTgwMDAxLCJzdWIiOiI2N2RhMDc3NmIwNWM4YTM4MGZhMWRjNjMiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.YOJT8fQFB-9oHq-5_vTEtaRHwuepKN0cjxvb6_aeeyw"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Headers para evitar bloqueios
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"
}

# Configuração manual do CORS
@app.after_request
def after_request(response):
    """Adiciona cabeçalhos CORS manualmente."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    return response

def obter_detalhes_filme_tmdb(titulo):
    """ Busca o pôster e o título oficial do filme no TMDB """
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": titulo,
        "language": "pt-BR"
    }
    resposta = requests.get(url, headers=HEADERS, params=params)
    
    if resposta.status_code == 200:
        resultados = resposta.json().get("results", [])
        if resultados:
            filme = resultados[0]
            poster_path = filme.get("poster_path")
            titulo_oficial = filme.get("title", titulo)  # Usa o título do TMDB, ou o original se não encontrar

            return {
                "poster": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://s.ltrbxd.com/static/img/empty-poster-35-vLShH7kq.png",
                "titulo": titulo_oficial
            }
    
    return {
        "poster": "https://s.ltrbxd.com/static/img/empty-poster-35-vLShH7kq.png",
        "titulo": titulo
    }

def obter_filmes_recentes():
    """ Faz scraping no Letterboxd para obter os últimos 4 filmes assistidos e suas avaliações """
    resposta = requests.get(URL_RECENTES, headers=HEADERS)

    if resposta.status_code != 200:
        return {"erro": f"Não foi possível acessar o Letterboxd (Status {resposta.status_code})"}

    soup = BeautifulSoup(resposta.text, "lxml")

    # Encontramos todas as linhas de filmes assistidos na página do diário
    filmes = soup.find_all("tr", class_="diary-entry-row")

    lista_filmes = []
    for filme in filmes[:4]:  # Pegamos os 4 mais recentes
        # Título do filme
        titulo_elemento = filme.find("td", class_="td-film-details")
        if titulo_elemento:
            titulo = titulo_elemento.find("a")
            titulo = titulo.text.strip() if titulo else "Título Desconhecido"
        else:
            titulo = "Título Desconhecido"

        # Avaliação do usuário no Letterboxd
        rating_elemento = filme.find("td", class_="td-rating")
        if rating_elemento:
            rating = rating_elemento.find("span", class_="rating")
            rating = rating.text.strip() if rating else "N/A"
        else:
            rating = "N/A"

        # Busca os detalhes do filme no TMDB (título e pôster)
        detalhes_filme = obter_detalhes_filme_tmdb(titulo)

        lista_filmes.append({
            "titulo": detalhes_filme["titulo"],
            "poster": detalhes_filme["poster"],
            "rating": rating
        })

    return lista_filmes

@app.route("/filmes/recentes", methods=["GET"])
def filmes_recentes():
    """ Endpoint para obter os filmes recentes """
    return jsonify(obter_filmes_recentes())

if __name__ == "__main__":
    app.run(debug=True)