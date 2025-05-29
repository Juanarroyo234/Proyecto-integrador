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

// Función para actualizar el escudo
function actualizarEscudo(selectId, imgId) {
    const equipoSeleccionado = document.getElementById(selectId).value;
    const imgElement = document.getElementById(imgId);
    if (escudos[equipoSeleccionado]) {
        imgElement.src = escudos[equipoSeleccionado];
        imgElement.alt = equipoSeleccionado;
        imgElement.style.display = 'inline'; // por si estaba oculto
    } else {
        imgElement.src = "";
        imgElement.alt = "";
        imgElement.style.display = 'none';
    }
}
