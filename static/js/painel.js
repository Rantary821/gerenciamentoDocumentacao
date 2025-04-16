// === Função global para carregar conteúdo dinamicamente ===
function carregarConteudo(url) {
    fetch(url)
        .then(res => res.text())
        .then(html => {
            const main = document.querySelector('.main-content');
            main.innerHTML = html;
        })
        .catch(err => {
            document.querySelector('.main-content').innerHTML = '<p>Erro ao carregar o conteúdo.</p>';
            console.error('Erro:', err);
        });
}

// === Tudo que depende do DOM ===
document.addEventListener('DOMContentLoaded', () => {
    console.log("Painel carregado com sucesso!");

    // === Rotas centralizadas ===
    window.rotas = {
        principal: '/painel-conteudo',  // antes era '/'
        formulario: '/gerar-formulario',
        cadastroModulo: '/cadastro-modulo',
        cadastroInversor: '/cadastro-inversor'
    };
    // === Aplica clique dinâmico aos links com data-rota ===
    document.querySelectorAll('.sidebar a[data-rota]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const rota = link.getAttribute('data-rota');
            if (rotas[rota]) {
                carregarConteudo(rotas[rota]);
            } else {
                console.warn(`Rota "${rota}" não encontrada.`);
            }
        });
    });

    // === Botão de toggle lateral (mobile) ===
    const toggleBtn = document.createElement('button');
    toggleBtn.classList.add('toggle-btn');
    toggleBtn.innerText = '☰';
    document.body.appendChild(toggleBtn);

    const sidebar = document.querySelector('.sidebar');
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });

    // === Campo de busca dinâmica ===
    const inputBusca = document.createElement('input');
    inputBusca.placeholder = 'Buscar projeto...';
    inputBusca.className = 'search-input';
    inputBusca.style.marginBottom = '20px';
    inputBusca.style.padding = '10px';
    inputBusca.style.width = '100%';

    const mainContent = document.querySelector('.main-content');
    mainContent.prepend(inputBusca);

    inputBusca.addEventListener('input', () => {
        const termo = inputBusca.value.toLowerCase();
        document.querySelectorAll('.projeto').forEach(proj => {
            proj.style.display = proj.textContent.toLowerCase().includes(termo) ? '' : 'none';
        });
    });

    // === Animação ao exibir projetos ===
    const projetos = document.querySelectorAll('.projeto');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animar');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    projetos.forEach(proj => observer.observe(proj));
});
