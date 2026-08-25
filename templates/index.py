<!DOCTYPE html>
<html lang="es">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Control de Documentación</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
          rel="stylesheet">

</head>

<body class="bg-light">

<nav class="navbar navbar-dark bg-dark">

    <div class="container">

        <span class="navbar-brand">
            Control de Documentación
        </span>

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


    <div class="d-flex justify-content-between align-items-center mb-4">

        <h2>Vencimientos</h2>

        <a href="{{ url_for('cargar') }}"
           class="btn btn-primary">

            + Cargar documentación

        </a>

    </div>


    <div class="row mb-4">

        <div class="col-md-4">

            <div class="card border-success shadow-sm">

                <div class="card-body">

                    <h5>Vigentes</h5>

                    <h2 class="text-success">
                        {{ total_vigentes }}
                    </h2>

                </div>

            </div>

        </div>


        <div class="col-md-4">

            <div class="card border-warning shadow-sm">

                <div class="card-body">

                    <h5>Por vencer</h5>

                    <h2 class="text-warning">
                        {{ total_por_vencer }}
                    </h2>

                </div>

            </div>

        </div>


        <div class="col-md-4">

            <div class="card border-danger shadow-sm">

                <div class="card-body">

                    <h5>Vencidos</h5>

                    <h2 class="text-danger">
                        {{ total_vencidos }}
                    </h2>

                </div>

            </div>

        </div>

    </div>


    <div class="card shadow-sm">

        <div class="card-body">

            <h4 class="mb-3">
                Categorías
            </h4>

            <div class="list-group">

                {% for item in resumen %}

                    <a href="{{ url_for('documentacion',
                                         nombre_hoja=item.nombre) }}"
                       class="list-group-item
                              list-group-item-action">

                        <div class="d-flex
                                    justify-content-between">

                            <strong>
                                {{ item.nombre }}
                            </strong>

                            <span>

                                <span class="badge bg-success">
                                    {{ item.vigentes }}
                                </span>

                                <span class="badge bg-warning text-dark">
                                    {{ item.por_vencer }}
                                </span>

                                <span class="badge bg-danger">
                                    {{ item.vencidos }}
                                </span>

                            </span>

                        </div>

                    </a>

                {% endfor %}

            </div>

        </div>

    </div>

</div>

</body>

</html>