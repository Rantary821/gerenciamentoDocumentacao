console.log("✅ mapa_localizacao.js carregado com sucesso!");

let mapa, marcador;

function buscarEndereco() {
    const cep = document.getElementById('cep').value.replace(/\D/g, '');
    if (cep.length !== 8) {
        console.warn("CEP incompleto.");
        return;
    }

    fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(response => response.json())
        .then(dados => {
            if (dados.erro) {
                console.warn("CEP não encontrado.");
                return;
            }

            const logradouro = dados.logradouro || '';
            const cidade = dados.localidade || '';
            const uf = dados.uf || '';

            console.log(`📦 Endereço encontrado: ${logradouro}, ${cidade}, ${uf}`);

            document.getElementById('endereco').value = logradouro;
            document.getElementById('cidade').value = cidade;

            const numero = document.querySelector('input[name="numero"]').value;
            if (logradouro && numero) {
                buscarCoordenadas(`${logradouro}, ${numero}, ${cidade}, ${uf}`);
            } else {
                buscarCoordenadasCidade();
            }
        })
        .catch(err => console.error("❌ Erro ao buscar o CEP:", err));
}

function atualizarLocalizacaoComNumero() {
    const logradouro = document.getElementById('endereco').value;
    const cidade = document.getElementById('cidade').value;
    const uf = document.getElementById('cep').value.substring(0, 2);
    const numero = document.querySelector('input[name="numero"]').value;

    if (!logradouro || !cidade || !numero) {
        console.warn("Dados de endereço incompletos.");
        return;
    }

    buscarCoordenadas(`${logradouro}, ${numero}, ${cidade}, ${uf}`);
}

function buscarCoordenadas(enderecoCompleto) {
    console.log(`🌐 Buscando coordenadas para: ${enderecoCompleto}`);

    fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(enderecoCompleto)}&format=json&limit=1`, {
        headers: { 'User-Agent': 'formulario-cpfl' }
    })
    .then(res => res.json())
    .then(resultado => {
        if (resultado.length > 0) {
            const { lat, lon } = resultado[0];
            console.log(`📍 Coordenadas encontradas: ${lat}, ${lon}`);
            inicializarMapa(parseFloat(lat), parseFloat(lon));
        } else {
            console.warn("❗ Endereço não encontrado com número. Tentando com cidade...");
            buscarCoordenadasCidade();
        }
    })
    .catch(err => console.error("❌ Erro ao buscar coordenadas:", err));
}

function buscarCoordenadasCidade() {
    const cidade = document.getElementById('cidade').value;
    const uf = document.getElementById('cep').value.substring(0, 2);
    if (!cidade || !uf) return;

    const cidadeCompleta = `${cidade}, ${uf}, Brasil`;
    console.log(`🌍 Buscando coordenadas da cidade: ${cidadeCompleta}`);

    fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(cidadeCompleta)}&format=json&limit=1`, {
        headers: { 'User-Agent': 'formulario-cpfl' }
    })
    .then(res => res.json())
    .then(resultado => {
        if (resultado.length > 0) {
            const { lat, lon } = resultado[0];
            console.log(`🏙️ Coordenadas da cidade: ${lat}, ${lon}`);
            inicializarMapa(parseFloat(lat), parseFloat(lon));
        } else {
            alert("Não foi possível localizar nem a cidade no mapa.");
        }
    })
    .catch(err => console.error("❌ Erro ao buscar coordenadas da cidade:", err));
}

function inicializarMapa(lat = -23.5505, lon = -46.6333) {
    const mapaDiv = document.getElementById("mapa");
    if (!mapaDiv) {
        console.warn("❌ Div #mapa não encontrada no DOM.");
        return;
    }

    console.log(`🗺️ Inicializando mapa em: ${lat}, ${lon}`);

    if (mapa && mapa._container) {
        console.log("⚠️ Mapa já existe. Apenas atualizando coordenadas.");
        mapa.setView([lat, lon], 15);
        marcador.setLatLng([lat, lon]);
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lon;
        setTimeout(() => mapa.invalidateSize(), 200);
        return;
    }

    // Inicializa o mapa
    mapa = L.map('mapa').setView([lat, lon], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © OpenStreetMap contributors'
    }).addTo(mapa);

    marcador = L.marker([lat, lon], { draggable: true }).addTo(mapa);
    marcador.on('dragend', function () {
        const pos = marcador.getLatLng();
        document.getElementById('latitude').value = pos.lat;
        document.getElementById('longitude').value = pos.lng;
    });

    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lon;

    setTimeout(() => mapa.invalidateSize(), 200);
}


function moverMarcadorManual() {
    const lat = parseFloat(document.getElementById('latitude').value);
    const lon = parseFloat(document.getElementById('longitude').value);
    if (isNaN(lat) || isNaN(lon)) {
        console.warn("Latitude ou longitude inválidas.");
        return;
    }

    console.log(`📌 Movendo marcador manualmente para: ${lat}, ${lon}`);

    if (!mapa) {
        inicializarMapa(lat, lon);
    } else {
        marcador.setLatLng([lat, lon]);
        mapa.setView([lat, lon], 15);
    }
}

// Vincula os eventos ao DOM carregado
document.addEventListener("DOMContentLoaded", function () {
    console.log("🧩 DOM totalmente carregado. Registrando eventos.");

    const campoCep = document.getElementById("cep");
    const campoNumero = document.querySelector('input[name="numero"]');
    const campoLat = document.getElementById("latitude");
    const campoLon = document.getElementById("longitude");

    campoCep.addEventListener("input", function () {
        if (this.value.replace(/\D/g, '').length === 8) {
            buscarEndereco();
        }
    });
    if (campoNumero) campoNumero.addEventListener("blur", atualizarLocalizacaoComNumero);
    if (campoLat) campoLat.addEventListener("blur", moverMarcadorManual);
    if (campoLon) campoLon.addEventListener("blur", moverMarcadorManual);
});
