function buscarEndereco() {
    const cepInput = document.getElementById("cep");
    if (!cepInput) return;

    const cep = cepInput.value.replace(/\D/g, '');
    if (cep.length !== 8) return;

    fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(response => response.json())
        .then(data => {
            if (data.erro) {
                alert("CEP não encontrado.");
                const campoEndereco = document.getElementById("endereco");
                const campoCidade = document.getElementById("cidade");
                if (campoEndereco) campoEndereco.value = "";
                if (campoCidade) campoCidade.value = "";
                return;
            }

            const campoEndereco = document.getElementById("endereco");
            const campoCidade = document.getElementById("cidade");

            if (campoEndereco && !campoEndereco.value) {
                campoEndereco.value = data.logradouro;
            }

            if (campoCidade) {
                campoCidade.value = data.localidade;
            }

            if (typeof atualizarLocalizacaoComCep === "function") {
                atualizarLocalizacaoComCep(data.logradouro, data.localidade);
            }
        })
        .catch(error => {
            console.error("Erro ao buscar o CEP:", error);
            alert("Erro ao buscar o CEP. Verifique sua conexão.");
        });
}

// Protege o addEventListener
document.addEventListener("DOMContentLoaded", function () {
    const campoCep = document.getElementById("cep");
    const campoEndereco = document.getElementById("endereco");
    const campoCidade = document.getElementById("cidade");

    if (campoCep && campoEndereco && campoCidade) {
        campoCep.addEventListener("input", function () {
            if (this.value.length < 8) {
                campoEndereco.value = "";
                campoCidade.value = "";
            }
        });

        campoCep.addEventListener("blur", buscarEndereco);
    }
});
