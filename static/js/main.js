document.addEventListener("DOMContentLoaded", () => {
  cargarEquipos();
  cargarTabla();
  mostrarPestana('prediccion'); // Mostrar predicción por defecto

  const btnFiltrar = document.getElementById('btn_filtrar_partidos');
  const btnLimpiar = document.getElementById('btn_limpiar_filtro');

  if (btnFiltrar) {
    btnFiltrar.addEventListener('click', () => {
      const filtroLocal = document.getElementById('filtro_local').value;
      const filtroVisitante = document.getElementById('filtro_visitante').value;
      cargarPartidos(filtroLocal, filtroVisitante);
    });
  }

  if (btnLimpiar) {
    btnLimpiar.addEventListener('click', () => {
      document.getElementById('filtro_local').value = '';
      document.getElementById('filtro_visitante').value = '';
      cargarPartidos();
    });
  }
});

// -----------------------------------------------------------
// Mostrar pestaña y cargar datos relacionados
function mostrarPestana(id) {
  const pestañas = ['prediccion', 'tabla', 'partidos', 'ganadosLocal', 'agregarPartido'];
  pestañas.forEach(pestana => {
    const el = document.getElementById(pestana);
    if (el) el.style.display = (pestana === id) ? 'block' : 'none';
  });

  if (id === 'tabla') {
    cargarTabla();
  } else if (id === 'partidos') {
    cargarPartidos();
    cargarFiltrosEquipos();
  } else if (id === 'ganadosLocal') {
    cargarGanadosLocal();
  }
}

// -----------------------------------------------------------
// EQUIPOS
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

// -----------------------------------------------------------
// PREDICCIÓN
async function hacerPrediccion() {
  const equipoLocal = document.getElementById("equipo_local").value;
  const equipoVisitante = document.getElementById("equipo_visitante").value;

  try {
    const respuesta = await fetch(`/predecir?equipo_local=${encodeURIComponent(equipoLocal)}&equipo_visitante=${encodeURIComponent(equipoVisitante)}`);

    if (respuesta.ok) {
      const resultado = await respuesta.json();
      document.getElementById("resultado").innerText = `Resultado: ${resultado.prediccion}`;
    } else {
      const error = await respuesta.json();
      document.getElementById("resultado").innerText = `Error: ${error.detail || "No se pudo predecir."}`;
    }
  } catch (error) {
    document.getElementById("resultado").innerText = `Error al predecir: ${error}`;
  }
}

// -----------------------------------------------------------
// TABLA POSICIONES
async function cargarTabla() {
  const contenedor = document.getElementById('contenedor-tabla');
  try {
    const res = await fetch('/tabla');
    if (!res.ok) throw new Error("Error al cargar la tabla");

    const data = await res.json();
    contenedor.innerHTML = crearTablaHTML(data);
    agregarEventosClickEquipos();
  } catch (error) {
    contenedor.innerHTML = `<p>Error: ${error.message}</p>`;
    console.error("Error cargando tabla:", error);
  }
}

// Evita múltiples event listeners al reemplazar los elementos antes de añadirlos
function agregarEventosClickEquipos() {
  const elementos = document.querySelectorAll('.equipo-click.nombre-equipo');

  elementos.forEach(elem => {
    // Clona el nodo para eliminar listeners previos y lo reemplaza
    const nuevoElem = elem.cloneNode(true);
    nuevoElem.style.cursor = 'pointer';
    elem.replaceWith(nuevoElem);
  });

  const nuevosElementos = document.querySelectorAll('.equipo-click.nombre-equipo');
  nuevosElementos.forEach(elem => {
    elem.addEventListener('click', () => {
      const nombreEquipo = elem.getAttribute('data-nombre');
      mostrarEstadisticas(nombreEquipo);
    });
  });
}

function crearTablaHTML(data) {
  if (!data.length) return "<p>No hay datos para mostrar</p>";

  // Asegúrate de definir escudos como un objeto global, ej:
  // const escudos = { "Equipo1": "url1", "Equipo2": "url2", ... };

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
        <td>
          <span class="equipo-click nombre-equipo" data-nombre="${equipo.equipo}">
            <img src="${escudos?.[equipo.equipo] || ''}" class="escudo-tabla" alt="Escudo ${equipo.equipo}" />
            ${equipo.equipo}
          </span>
        </td>
        <td>${equipo.puntos}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  return html;
}

// -----------------------------------------------------------
// PARTIDOS
async function cargarPartidos(filtroLocal = '', filtroVisitante = '') {
  const contenedor = document.getElementById('contenedor-partidos');
  try {
    const res = await fetch('/partidos');
    if (!res.ok) throw new Error("Error al cargar los partidos");

    let data = await res.json();

    if (filtroLocal) {
      data = data.filter(p => p.equipo_local === filtroLocal);
    }
    if (filtroVisitante) {
      data = data.filter(p => p.equipo_visitante === filtroVisitante);
    }

    contenedor.innerHTML = crearPartidosHTML(data);
  } catch (error) {
    contenedor.innerHTML = `<p>Error: ${error.message}</p>`;
    console.error("Error cargando partidos:", error);
  }
}

function crearPartidosHTML(data) {
  if (!data.length) return "<p>No hay partidos para mostrar</p>";

  let html = `
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Equipo Local</th>
          <th>Goles Local</th>
          <th>Equipo Visitante</th>
          <th>Goles Visitante</th>
          <th>Fecha</th>
        </tr>
      </thead>
      <tbody>
  `;

  data.forEach((partido, index) => {
    html += `
      <tr>
        <td>${index + 1}</td>
        <td>${partido.equipo_local}</td>
        <td>${partido.goles_local}</td>
        <td>${partido.equipo_visitante}</td>
        <td>${partido.goles_visitante}</td>
        <td>${partido.fecha ? new Date(partido.fecha).toLocaleDateString() : '-'}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  return html;
}

// -----------------------------------------------------------
// GANADOS COMO LOCAL
async function cargarGanadosLocal() {
  const contenedor = document.getElementById('contenedor-ganadosLocal');
  try {
    const res = await fetch('/ganados-local');
    if (!res.ok) throw new Error("Error al cargar partidos ganados por local");

    const data = await res.json();
    contenedor.innerHTML = crearTablaGanadosLocal(data);
  } catch (error) {
    contenedor.innerHTML = `<p>Error: ${error.message}</p>`;
    console.error(error);
  }
}

function crearTablaGanadosLocal(data) {
  if (!data.length) return "<p>No hay partidos ganados por local para mostrar</p>";

  let html = `
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Equipo Local</th>
          <th>Equipo Visitante</th>
          <th>Goles Local</th>
          <th>Goles Visitante</th>
        </tr>
      </thead>
      <tbody>
  `;

  data.forEach((partido, index) => {
    html += `
      <tr>
        <td>${index + 1}</td>
        <td>${partido.equipo_local}</td>
        <td>${partido.equipo_visitante}</td>
        <td>${partido.goles_local ?? 0}</td>
        <td>${partido.goles_visitante ?? 0}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  return html;
}

// -----------------------------------------------------------
// AGREGAR PARTIDO
const formPartido = document.getElementById('form-partido');
const mensajeForm = document.getElementById('mensaje_form_partido');

if (formPartido) {
  formPartido.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validación simple
    if (!formPartido.equipo_local.value || !formPartido.equipo_visitante.value) {
      mensajeForm.textContent = 'Seleccione ambos equipos.';
      mensajeForm.style.color = 'red';
      return;
    }
    if (formPartido.equipo_local.value === formPartido.equipo_visitante.value) {
      mensajeForm.textContent = 'Los equipos no pueden ser iguales.';
      mensajeForm.style.color = 'red';
      return;
    }
    if (isNaN(parseInt(formPartido.goles_local.value)) || isNaN(parseInt(formPartido.goles_visitante.value))) {
      mensajeForm.textContent = 'Ingrese goles válidos.';
      mensajeForm.style.color = 'red';
      return;
    }

    const data = {
      equipo_local: formPartido.equipo_local.value,
      equipo_visitante: formPartido.equipo_visitante.value,
      goles_local: parseInt(formPartido.goles_local.value),
      goles_visitante: parseInt(formPartido.goles_visitante.value),
      resultado: formPartido.resultado.value,
    };

    const btnEnviar = formPartido.querySelector('button[type="submit"]');
    btnEnviar.disabled = true;

    try {
      const response = await fetch('/partidos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al agregar el partido');
      }

      mensajeForm.textContent = 'Partido agregado correctamente.';
      mensajeForm.style.color = 'green';
      formPartido.reset();

      // Actualizar lista partidos si se está viendo esa pestaña
      if (document.getElementById('partidos').style.display === 'block') {
        cargarPartidos();
      }
    } catch (error) {
      mensajeForm.textContent = `Error: ${error.message}`;
      mensajeForm.style.color = 'red';
    } finally {
      btnEnviar.disabled = false;
    }
  });
}

// -----------------------------------------------------------
// FILTROS para partidos
async function cargarFiltrosEquipos() {
  try {
    const res = await fetch('/equipos');
    if (!res.ok) throw new Error("Error al obtener equipos para filtros");
    const data = await res.json();
    const equipos = data.equipos || [];

    const filtroLocal = document.getElementById('filtro_local');
    const filtroVisitante = document.getElementById('filtro_visitante');
    filtroLocal.innerHTML = `<option value="">--Todos--</option>`;
    filtroVisitante.innerHTML = `<option value="">--Todos--</option>`;

    equipos.forEach(equipo => {
      filtroLocal.innerHTML += `<option value="${equipo}">${equipo}</option>`;
      filtroVisitante.innerHTML += `<option value="${equipo}">${equipo}</option>`;
    });
  } catch (error) {
    console.error("Error cargando filtros de equipos:", error);
  }
}

// -----------------------------------------------------------
// Mostrar estadísticas y gráfico con Chart.js
async function mostrarEstadisticas(equipo) {
  const contenedor = document.getElementById('contenedor-estadisticas');
  contenedor.innerHTML = `<h2>Estadísticas de ${equipo}</h2><canvas id="graficoEstadisticas"></canvas>`;

  try {
    const res = await fetch(`/estadisticas/${encodeURIComponent(equipo)}`);
    if (!res.ok) throw new Error("Error al cargar estadísticas");

    const data = await res.json();

    const ctx = document.getElementById('graficoEstadisticas').getContext('2d');

    // Si ya existe un gráfico, destruirlo para evitar superposición
    if (window.graficoActual) {
      window.graficoActual.destroy();
    }

    window.graficoActual = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Victorias', 'Empates', 'Derrotas'],
        datasets: [{
          label: `Resultados de ${equipo}`,
          data: [data.victorias, data.empates, data.derrotas],
          backgroundColor: ['#4caf50', '#ffeb3b', '#f44336'],
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true, precision: 0 }
        }
      }
    });
  } catch (error) {
    contenedor.innerHTML = `<p>Error al cargar estadísticas: ${error.message}</p>`;
    console.error(error);
  }
}

// -----------------------------------------------------------
// Actualizar escudo al cambiar selección
function actualizarEscudo(selectId, escudoId) {
  const select = document.getElementById(selectId);
  const escudo = document.getElementById(escudoId);
  if (!select || !escudo) return;

  select.addEventListener('change', () => {
    const equipoSeleccionado = select.value;
    // Cambia la ruta del escudo, define globalmente "escudos" con URLs
    escudo.src = escudos?.[equipoSeleccionado] || '';
  });

  // Set inicial
  escudo.src = escudos?.[select.value] || '';
}
