let mapa, marcador;

function buscarEndereco() {
    const cep = document.getElementById('cep').value.replace(/\D/g, '');
    if (cep.length !== 8) return;

    fetch(`https://viacep.com.br/ws/${cep}/json/`)
        .then(response => response.json())
        .then(dados => {
            if (dados.erro) return;

            const logradouro = dados.logradouro || '';
            const cidade = dados.localidade || '';
            const uf = dados.uf || '';
            
            document.getElementById('endereco').value = logradouro;
            document.getElementById('cidade').value = cidade;

            if (logradouro) {
                const numero = document.querySelector('input[name="numero"]').value;
                if (numero) {
                    buscarCoordenadas(`${logradouro}, ${numero}, ${cidade}, ${uf}`);
                }
            }
        });
}

function atualizarLocalizacaoComNumero() {
    const logradouro = document.getElementById('endereco').value;
    const cidade = document.getElementById('cidade').value;
    const uf = document.getElementById('cep').value.substring(0, 2);
    const numero = document.querySelector('input[name="numero"]').value;

    if (!logradouro || !cidade || !numero) return;

    buscarCoordenadas(`${logradouro}, ${numero}, ${cidade}, ${uf}`);
}

function buscarCoordenadas(enderecoCompleto) {
    fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(enderecoCompleto)}&format=json&limit=1`, {
        headers: { 'User-Agent': 'formulario-cpfl' }
    })
    .then(res => res.json())
    .then(resultado => {
        if (resultado.length > 0) {
            const { lat, lon } = resultado[0];
            inicializarMapa(parseFloat(lat), parseFloat(lon));
        } else {
            console.warn("Não encontrou localização precisa. Tentando pela cidade...");
            buscarCoordenadasCidade();
        }
    });
}
function buscarCoordenadasCidade() {
    const cidade = document.getElementById('cidade').value;
    const uf = document.getElementById('cep').value.substring(0, 2);
    if (!cidade || !uf) return;

    const cidadeCompleta = `${cidade}, ${uf}, Brasil`;

    fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(cidadeCompleta)}&format=json&limit=1`, {
        headers: { 'User-Agent': 'formulario-cpfl' }
    })
    .then(res => res.json())
    .then(resultado => {
        if (resultado.length > 0) {
            const { lat, lon } = resultado[0];
            inicializarMapa(parseFloat(lat), parseFloat(lon));
        } else {
            alert("Não foi possível localizar nem a cidade no mapa.");
        }
    });
}

function inicializarMapa(lat = -23.5505, lon = -46.6333) {
    if (!mapa) {
        mapa = L.map('mapa').setView([lat, lon], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data © OpenStreetMap contributors'
        }).addTo(mapa);

        marcador = L.marker([lat, lon], { draggable: true }).addTo(mapa);
        marcador.on('dragend', function (e) {
            const pos = marcador.getLatLng();
            document.getElementById('latitude').value = pos.lat;
            document.getElementById('longitude').value = pos.lng;
        });

        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lon;
    } else {
        mapa.setView([lat, lon], 15);
        marcador.setLatLng([lat, lon]);
    }
}

function moverMarcadorManual() {
    const lat = parseFloat(document.getElementById('latitude').value);
    const lon = parseFloat(document.getElementById('longitude').value);
    if (isNaN(lat) || isNaN(lon)) return;

    if (!mapa) {
        inicializarMapa(lat, lon);
    } else {
        marcador.setLatLng([lat, lon]);
        mapa.setView([lat, lon], 15);
    }
}
