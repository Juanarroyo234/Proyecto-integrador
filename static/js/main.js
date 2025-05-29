// main.js

document.addEventListener('DOMContentLoaded', () => {
    const btnMostrarTabla = document.getElementById('btn-mostrar-tabla');
    const contenedorTabla = document.getElementById('contenedor-tabla');
    let tablaVisible = false;

    btnMostrarTabla.addEventListener('click', async () => {
        if (!tablaVisible) {
            btnMostrarTabla.textContent = "Ocultar Tabla";
            await cargarTabla();
            contenedorTabla.style.display = 'block';
        } else {
            btnMostrarTabla.textContent = "Mostrar Tabla";
            contenedorTabla.style.display = 'none';
            contenedorTabla.innerHTML = '';  // Limpiar tabla al ocultar
        }
        tablaVisible = !tablaVisible;
    });

    async function cargarTabla() {
        try {
            const res = await fetch('/tabla');
            if (!res.ok) throw new Error('Error al cargar la tabla');
            const data = await res.json();

            // Suponiendo que data es un array de objetos con propiedades como equipo, puntos, etc.
            contenedorTabla.innerHTML = crearTablaHTML(data);

        } catch (error) {
            contenedorTabla.innerHTML = `<p>Error al cargar la tabla: ${error.message}</p>`;
        }
    }

    function crearTablaHTML(data) {
        if (!data.length) return "<p>No hay datos para mostrar</p>";

        let html = `
            <table class="tabla-posiciones">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Equipo</th>
                        <th>Partidos Jugados</th>
                        <th>Ganados</th>
                        <th>Empatados</th>
                        <th>Perdidos</th>
                        <th>Goles Favor</th>
                        <th>Goles Contra</th>
                        <th>Diferencia</th>
                        <th>Puntos</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.forEach((equipo, index) => {
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${equipo.equipo}</td>
                    <td>${equipo.partidos_jugados}</td>
                    <td>${equipo.ganados}</td>
                    <td>${equipo.empatados}</td>
                    <td>${equipo.perdidos}</td>
                    <td>${equipo.goles_favor}</td>
                    <td>${equipo.goles_contra}</td>
                    <td>${equipo.diferencia_goles}</td>
                    <td>${equipo.puntos}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        return html;
    }
});
