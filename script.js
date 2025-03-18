async function carregarFilmes() {
    try {
        const resposta = await fetch("http://127.0.0.1:5000/filmes/recentes");
        
        // Verifica se a resposta é válida
        if (!resposta.ok) {
            throw new Error("Erro ao carregar filmes.");
        }

        const filmes = await resposta.json();
        
        let html = "";
        filmes.forEach(filme => {
            html += `
                <div class="filme">
                    <img src="${filme.poster}" alt="${filme.titulo}" onerror="this.src='https://s.ltrbxd.com/static/img/empty-poster-35-vLShH7kq.png'">
                    <p>${filme.titulo}</p>
                </div>
            `;
        });

        document.getElementById("lista-recentes").innerHTML = html;
    } catch (erro) {
        console.error(erro);
        document.getElementById("lista-recentes").innerHTML = "<p>Erro ao carregar filmes.</p>";
    }
}

// Chamar a função ao carregar a página
carregarFilmes();

// Atualizar filmes a cada 5 minutos (300.000 milissegundos)
setInterval(carregarFilmes, 300000);