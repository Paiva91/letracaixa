from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

# Cria a instância do Flask
app = Flask(__name__)

# Configuração
USUARIO_LETTERBOXD = "wiseking"  # Substitua pelo seu usuário do Letterboxd
URL_RECENTES = f"https://letterboxd.com/{USUARIO_LETTERBOXD}/films/diary/"
TMDB_API_KEY = "SUA_CHAVE_DO_TMDB_AQUI"  # Substitua pela sua chave do TMDb
TMDB_URL = "https://api.themoviedb.org/3/search/movie"

# Headers para evitar bloqueios
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Configuração manual do CORS
@app.after_request
def after_request(response):
    """Adiciona cabeçalhos CORS manualmente."""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET")
    return response

def buscar_poster_no_tmdb(titulo):
    """ Busca o pôster de um filme no TMDb """
    params = {
        "api_key": TMDB_API_KEY,
        "query": titulo,
        "language": "pt-BR"  # Opcional: busca em português
    }
    resposta = requests.get(TMDB_URL, params=params)
    if resposta.status_code == 200:
        dados = resposta.json()
        if dados["results"]:
            # Retorna a URL do pôster do primeiro resultado
            poster_path = dados["results"][0]["poster_path"]
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://s.ltrbxd.com/static/img/empty-poster-35-vLShH7kq.png"  # Placeholder padrão

def obter_filmes_recentes():
    """ Faz scraping no Letterboxd para obter os últimos 4 filmes assistidos """
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

        # Busca o pôster no TMDb
        poster_url = buscar_poster_no_tmdb(titulo)

        lista_filmes.append({
            "titulo": titulo,
            "poster": poster_url
        })

    return lista_filmes

@app.route("/filmes/recentes", methods=["GET"])
def filmes_recentes():
    """ Endpoint para obter os filmes recentes """
    return jsonify(obter_filmes_recentes())

if __name__ == "__main__":
    app.run(debug=True)