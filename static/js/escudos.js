const escudos = {
    "1. FC Koeln": "/static/escudos/1_fc_koeln.png",
    "1. FC Nürnberg": "/static/escudos/1_fc_nurnberg.png",
    "1. FC Union Berlin": "/static/escudos/1_fc_union_berlin.png",
    "1. FSV Mainz 05": "/static/escudos/1_fsv_mainz_05.png",
    "AC Ajaccio": "/static/escudos/ac_ajaccio.png",
    "AC Milan": "/static/escudos/ac_milan.png",
    "ACR Messina": "/static/escudos/acr_messina.png",
    "AS Roma": "/static/escudos/as_roma.png",
    "Aachen": "/static/escudos/aachen.png",
    "Aalen": "/static/escudos/aalen.png",
    "Academica": "/static/escudos/academica.png",
    "Accrington": "/static/escudos/accrington.png",
    "Adana Demirspor": "/static/escudos/adana_demirspor.png",
    "Adanaspor": "/static/escudos/adanaspor.png",
    "Ajax": "/static/escudos/ajax.png"
};

document.addEventListener("DOMContentLoaded", () => {
    const selectLocal = document.getElementById("equipo_local");
    const selectVisitante = document.getElementById("equipo_visitante");

    Object.keys(escudos).forEach(equipo => {
        const option1 = new Option(equipo, equipo);
        const option2 = new Option(equipo, equipo);
        selectLocal.appendChild(option1);
        selectVisitante.appendChild(option2);
    });
});

function actualizarEscudo(selectId, imgId) {
    const equipo = document.getElementById(selectId).value;
    const img = document.getElementById(imgId);
    if (escudos[equipo]) {
        img.src = escudos[equipo];
        img.style.display = 'inline';
        img.alt = equipo;
    } else {
        img.style.display = 'none';
        img.src = '';
        img.alt = '';
    }
}