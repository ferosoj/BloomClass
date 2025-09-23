<?php include('header.php'); ?>
<style>
        body {
    background-color: #f1d0a3;
        }
</style>
<div class="container my-4">
    <!-- Carrusel con títulos -->
    <div id="carousel1" class="carousel slide shadow rounded" data-bs-ride="carousel" data-bs-interval="3000">
        <!-- Indicadores -->
        <div class="carousel-indicators">
            <button type="button" data-bs-target="#carousel1" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>
            <button type="button" data-bs-target="#carousel1" data-bs-slide-to="1" aria-label="Slide 2"></button>
            <button type="button" data-bs-target="#carousel1" data-bs-slide-to="2" aria-label="Slide 3"></button>
        </div>

        <!-- Slides -->
        <div class="carousel-inner">
            <div class="carousel-item active">
                <img src="Imagenes/banner1.png" 
                class="d-block img-fluid" 
                style="width: auto; height: auto; max-height: none; object-fit: contain;" 
                alt="Ciencias Naturales">
            </div>
            
            <div class="carousel-item active">
                <img src="Imagenes/banner2.png" 
                class="d-block img-fluid" 
                style="width: auto; height: auto; max-height: none; object-fit: contain;" 
                alt="Matemáticas">
            </div>

            <div class="carousel-item active">
                <img src="Imagenes/banner3.png" 
                class="d-block img-fluid" 
                style="width: auto; height: auto; max-height: none; object-fit: contain;" 
                alt="Optativos">
            </div>
        </div>

        <!-- Controles -->
        <button class="carousel-control-prev" type="button" data-bs-target="#carousel1" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Anterior</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#carousel1" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Siguiente</span>
        </button>
    </div>
</div>


<!-- Sección Bienvenida y Catálogo -->
<div class="container my-5">
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="card shadow h-100">
                <img src="Imagenes/curriculum.png" class="card-img-top" alt="curriculum">
                <div class="card-body">
                    <h4 class="card-title">Lineamientos con Bases Curriculares</h4>
                    <p class="card-text">Revisa aquí el currículum nacional para cada asignatura y curso, y verifica que todos nuestros cursos están constantemente actualizados.</p>
                <?php
                $link = "https://www.curriculumnacional.cl/recursos/bases-curriculares-1-6-basico";
                echo "<a href='$link' class='btn btn-primary'>Ver Detalles</a>";
                ?>
                </div>
            </div>
        </div>
        <div class="col-md-6 mb-4">
            <div class="card shadow h-100">
                <a href="###">
                    <img src="Imagenes/optativos.jpg" class="card-img-top" alt="Optativos">
                </a>
                <div class="card-body">
                    <h4 class="card-title">Explora nuestro catálogo de cursos optativos</h4>
                    <p class="card-text">¡Contamos con un variada selección de cursos y actividades optativas para todas las edades!</p>
                    <a href="###" class="btn btn-primary">Ver Catálogo</a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Servicios Destacados -->
<div class="container my-5">
    <h3 class="text-center mb-4">¿Por qué elegirnos?</h3>
    <div class="row text-center">
        <div class="col-md-4 mb-3">
            <div class="p-4 bg-light shadow-sm rounded">
                <i class="fa-sharp-duotone fa-thin fa-globe" style="--fa-primary-color: #dd925f; --fa-secondary-color: #dd925f;"></i>
                <h5>Disponibilidad inmediata</h5>
                <p>Siempre puedes acceder a nuestros cursos, independientemente de dónde te encuentres.</p>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="p-4 bg-light shadow-sm rounded">
                <i class="fa-sharp-duotone fa-thin fa-file" style="--fa-primary-color: #eaa361; --fa-secondary-color: #eaa361;"></i>
                <h5>Cursos actualizados</h5>
                <p>Las unidades de cada curso se actulizan paralelamente al curriculum nacional, asi nos aseguramos que el contenido es veridico.</p>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="p-4 bg-light shadow-sm rounded">
               <i class="fa-sharp-duotone fa-solid fa-alien-8bit" style="--fa-primary-color: #dc9d56; --fa-secondary-color: #dc9d56;"></i>
                <h5>Diversión y aprendizaje</h5>
                <p>Actividades y juegos didácticos para todas las edades</p>
            </div>
        </div>
    </div>
</div>
<?php include('footer.php'); ?>
