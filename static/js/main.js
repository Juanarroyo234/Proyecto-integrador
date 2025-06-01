document.addEventListener("DOMContentLoaded", () => {
  cargarEquipos();
  cargarTabla();
  mostrarPestana('prediccion'); // Mostrar predicción por defecto
});

function mostrarPestana(id) {
  document.getElementById('prediccion').style.display = id === 'prediccion' ? 'block' : 'none';
  document.getElementById('tabla').style.display = id === 'tabla' ? 'block' : 'none';

    if (id === 'tabla') {
        cargarTabla();
    }
}

async function cargarEquipos() {
  try {
    const res = await fetch('/equipos');
    if (!res.ok) throw new Error("Error al obtener equipos");
    const data = await res.json();
    const equipos = data.equipos || [];

    const selectLocal = document.getElementById('equipo_local');
    const selectVisitante = document.getElementById('equipo_visitante');
    selectLocal.innerHTML = '';
    selectVisitante.innerHTML = '';

    equipos.forEach(equipo => {
      const optionLocal = document.createElement('option');
      optionLocal.value = equipo;
      optionLocal.textContent = equipo;
      selectLocal.appendChild(optionLocal);

      const optionVisitante = document.createElement('option');
      optionVisitante.value = equipo;
      optionVisitante.textContent = equipo;
      selectVisitante.appendChild(optionVisitante);
    });

    actualizarEscudo('equipo_local', 'escudo_local');
    actualizarEscudo('equipo_visitante', 'escudo_visitante');
  } catch (error) {
    console.error(error);
    alert("No se pudieron cargar los equipos.");
  }
}

async function hacerPrediccion() {
  const local = document.getElementById('equipo_local').value;
  const visitante = document.getElementById('equipo_visitante').value;
  const resultadoDiv = document.getElementById('resultado');

  if (!local || !visitante) {
    resultadoDiv.textContent = "Por favor selecciona ambos equipos.";
    return;
  }

  try {
    const res = await fetch(`/predecir?equipo_local=${encodeURIComponent(local)}&equipo_visitante=${encodeURIComponent(visitante)}`);
    if (!res.ok) throw new Error("Error en la predicción");
    const data = await res.json();

    if(data.error){
      resultadoDiv.textContent = data.error;
    } else {
      resultadoDiv.textContent = `Predicción: ${data.equipo_local} vs ${data.equipo_visitante} → Resultado: ${data.prediccion}`;
    }
  } catch (error) {
    resultadoDiv.textContent = "Error al obtener la predicción.";
    console.error(error);
  }
}

async function cargarTabla() {
  const contenedor = document.getElementById('contenedor-tabla');
  try {
    const res = await fetch('/tabla');
    console.log("Respuesta de /tabla:", res);
    if (!res.ok) throw new Error("Error al cargar la tabla");

    const data = await res.json();
    console.log("Datos recibidos:", data);
    contenedor.innerHTML = crearTablaHTML(data);
  } catch (error) {
    contenedor.innerHTML = `<p>Error: ${error.message}</p>`;
    console.error("Error cargando tabla:", error);
  }
}


function crearTablaHTML(data) {
    if (!data.length) return "<p>No hay datos para mostrar</p>";

    let html = `
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Equipo</th>
                    <th>PTS</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.forEach((equipo, index) => {
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${equipo.equipo}</td>
                <td>${equipo.puntos}</td>
            </tr>
        `;
    });

    html += "</tbody></table>";
    return html;
}
