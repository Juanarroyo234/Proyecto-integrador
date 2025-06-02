document.addEventListener("DOMContentLoaded", () => {
  cargarEquipos();
  cargarTabla();
  mostrarPestana('prediccion'); // Mostrar predicción por defecto
});

function mostrarPestana(id) {
  document.getElementById('prediccion').style.display = id === 'prediccion' ? 'block' : 'none';
  document.getElementById('tabla').style.display = id === 'tabla' ? 'block' : 'none';
  document.getElementById('partidos').style.display = id === 'partidos' ? 'block' : 'none';
  document.getElementById('ganadosLocal').style.display = id === 'ganadosLocal' ? 'block' : 'none';
  document.getElementById('agregarPartido').style.display = id === 'agregarPartido' ? 'block' : 'none';

  if (id === 'tabla') {
    cargarTabla();
  } else if (id === 'partidos') {
    cargarPartidos();
    cargarFiltrosEquipos();  // <-- Agregado para cargar filtros al mostrar partidos
  } else if (id === 'ganadosLocal') {
    cargarGanadosLocal();
  }
}

// --- Código existente ---

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


async function cargarTabla() {
  const contenedor = document.getElementById('contenedor-tabla');
  try {
    const res = await fetch('/tabla');
    if (!res.ok) throw new Error("Error al cargar la tabla");

    const data = await res.json();
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

// GANADOS LOCAL
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

// --- NUEVO: Formulario agregar partido ---
const formPartido = document.getElementById('form-partido');
const mensajeForm = document.getElementById('mensaje_form_partido');

if (formPartido) {
  formPartido.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
      equipo_local: formPartido.equipo_local.value,
      equipo_visitante: formPartido.equipo_visitante.value,
      goles_local: parseInt(formPartido.goles_local.value),
      goles_visitante: parseInt(formPartido.goles_visitante.value),
      resultado: formPartido.resultado.value,
    };

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
    } catch (error) {
      mensajeForm.textContent = error.message;
      mensajeForm.style.color = 'red';
    }
  });
}

// --- NUEVO: FILTROS PARA PARTIDOS ---
async function cargarFiltrosEquipos() {
  try {
    const res = await fetch('/equipos');
    if (!res.ok) throw new Error("Error al obtener equipos");
    const data = await res.json();
    const equipos = data.equipos || [];

    const filtroLocal = document.getElementById('filtro_local');
    const filtroVisitante = document.getElementById('filtro_visitante');
    filtroLocal.innerHTML = '<option value="">Todos</option>';
    filtroVisitante.innerHTML = '<option value="">Todos</option>';

    equipos.forEach(equipo => {
      const optionLocal = document.createElement('option');
      optionLocal.value = equipo;
      optionLocal.textContent = equipo;
      filtroLocal.appendChild(optionLocal);

      const optionVisitante = document.createElement('option');
      optionVisitante.value = equipo;
      optionVisitante.textContent = equipo;
      filtroVisitante.appendChild(optionVisitante);
    });
  } catch (error) {
    console.error(error);
    alert("No se pudieron cargar los equipos para filtro.");
  }
}

// Botones filtrar y limpiar filtro partidos
document.addEventListener("DOMContentLoaded", () => {
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
