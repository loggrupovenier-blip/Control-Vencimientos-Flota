<!DOCTYPE html>
<html lang="es">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{{ nombre_hoja }}</title>

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


    {% with messages = get_flashed_messages(with_categories=true) %}

        {% for category, message in messages %}

            <div class="alert alert-{{ category }}">
                {{ message }}
            </div>

        {% endfor %}

    {% endwith %}


    <div class="d-flex
                justify-content-between
                align-items-center
                mb-4">

        <h2>
            {{ nombre_hoja }}
        </h2>

        <a href="{{ url_for('cargar') }}"
           class="btn btn-primary">

            + Cargar

        </a>

    </div>


    <div class="card shadow-sm">

        <div class="card-body">

            <div class="table-responsive">

                <table class="table table-hover">

                    <thead>

                        <tr>

                            <th>Patente</th>

                            <th>Documento</th>

                            <th>Vencimiento</th>

                            <th>Estado</th>

                            <th>Foto</th>

                        </tr>

                    </thead>


                    <tbody>

                    {% for registro in registros %}

                        <tr>

                            <td>
                                <strong>
                                    {{ registro.patente }}
                                </strong>
                            </td>

                            <td>
                                {{ registro.documento }}
                            </td>

                            <td>
                                {{ registro.fecha }}
                            </td>

                            <td>

                                {% if registro.estado == "VIGENTE" %}

                                    <span class="badge bg-success">
                                        VIGENTE
                                    </span>

                                {% elif registro.estado == "POR VENCER" %}

                                    <span class="badge bg-warning text-dark">
                                        POR VENCER
                                    </span>

                                {% elif registro.estado == "VENCIDO" %}

                                    <span class="badge bg-danger">
                                        VENCIDO
                                    </span>

                                {% else %}

                                    <span class="badge bg-secondary">
                                        SIN FECHA
                                    </span>

                                {% endif %}

                            </td>


                            <td>

                                {% if registro.foto %}

                                    <a href="{{ registro.foto }}"
                                       target="_blank"
                                       class="btn btn-sm btn-outline-primary">

                                        Ver documento

                                    </a>

                                {% else %}

                                    -

                                {% endif %}

                            </td>

                        </tr>

                    {% else %}

                        <tr>

                            <td colspan="5"
                                class="text-center">

                                No hay documentación cargada.

                            </td>

                        </tr>

                    {% endfor %}

                    </tbody>

                </table>

            </div>

        </div>

    </div>

</div>


</body>

</html>