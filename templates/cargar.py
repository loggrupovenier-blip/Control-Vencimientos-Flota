<!DOCTYPE html>
<html lang="es">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Cargar documentación</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
          rel="stylesheet">

</head>


<body class="bg-light">


<nav class="navbar navbar-dark bg-dark">

    <div class="container">

        <a href="{{ url_for('index') }}"
           class="navbar-brand">

            Control de Documentación

        </a>

    </div>

</nav>


<div class="container py-4">

    <div class="card shadow">

        <div class="card-body">

            <h2 class="mb-4">
                Cargar documentación
            </h2>


            {% with messages = get_flashed_messages(with_categories=true) %}

                {% for category, message in messages %}

                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>

                {% endfor %}

            {% endwith %}


            <form method="POST"
                  action="{{ url_for('guardar') }}"
                  enctype="multipart/form-data">


                <div class="mb-3">

                    <label class="form-label">
                        Categoría *
                    </label>

                    <select name="hoja"
                            class="form-select"
                            required>

                        <option value="">
                            Seleccionar...
                        </option>

                        {% for hoja in hojas %}

                            <option value="{{ hoja }}">
                                {{ hoja }}
                            </option>

                        {% endfor %}

                    </select>

                </div>


                <div class="mb-3">

                    <label class="form-label">
                        Patente *
                    </label>

                    <input type="text"
                           name="patente"
                           class="form-control"
                           placeholder="Ejemplo: AB123CD"
                           required>

                </div>


                <div class="mb-3">

                    <label class="form-label">
                        Documento *
                    </label>

                    <input type="text"
                           name="documento"
                           class="form-control"
                           placeholder="Ejemplo: VTV"
                           required>

                </div>


                <div class="mb-3">

                    <label class="form-label">
                        Fecha de vencimiento *
                    </label>

                    <input type="date"
                           name="fecha_vencimiento"
                           class="form-control"
                           required>

                </div>


                <div class="mb-4">

                    <label class="form-label">
                        Foto del documento *
                    </label>

                    <input type="file"
                           name="foto"
                           class="form-control"
                           accept=".jpg,.jpeg,.png,.webp,.pdf"
                           required>

                    <div class="form-text">

                        Obligatorio. Máximo 10 MB.

                    </div>

                </div>


                <div class="d-flex gap-2">

                    <a href="{{ url_for('index') }}"
                       class="btn btn-secondary">

                        Cancelar

                    </a>

                    <button type="submit"
                            class="btn btn-primary">

                        Guardar documentación

                    </button>

                </div>

            </form>

        </div>

    </div>

</div>


</body>

</html>