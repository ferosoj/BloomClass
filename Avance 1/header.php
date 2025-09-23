<?php
session_start();

// Calcular cantidad total de productos en el carrito
$totalItems = 0;
if (isset($_SESSION['carrito'])) {
    foreach ($_SESSION['carrito'] as $cantidad) {
        if (is_array($cantidad)) {
            $totalItems += $cantidad['cantidad'] ?? 0;
        } else {
            $totalItems += $cantidad;
        }
    }
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BloomClass</title>

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    
<nav class="navbar navbar-expand-lg navbar-light bg-light shadow-sm px-4">
    <a class="navbar-brand d-flex align-items-center" href="BloomClass.php">
        <img src="Imagenes/logo.png" width="100" height="68" class="d-inline-block align-top me-2" alt="Logo">
    </a>
    
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
    </button>
    
    <div class="container-fluid d-flex justify-content-between">
    <ul class="navbar-nav">
    <li class="nav-item">
        <a class="nav-link active" href="#">Inicio</a>
    </li>
    <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">Cursos</a>
            <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="#">1° Básico</a></li>
            <li><a class="dropdown-item" href="#">2° Básico</a></li>
            <li><a class="dropdown-item" href="#">3° Básico</a></li>
            <li><a class="dropdown-item" href="#">4° Básico</a></li>
            <li><a class="dropdown-item" href="#">5° Básico</a></li>
            <li><a class="dropdown-item" href="#">6° Básico</a></li>
            </ul>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="#">Recursos</a>
    </li>
    <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">Material Optativo</a>
            <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="#">Cursos Optativos</a></li>
            <li><a class="dropdown-item" href="#">Recursos Gubernamentales</a></li>
            <li><a class="dropdown-item" href="#">Biblioteca</a></li>
            </ul>
    </li>
    <li class="nav-item">
        <a class="nav-link" href="#">Nosotros</a>
    </li>
    <form class="d-flex" style="margin-left: auto; margin-right: 20px;">
      <input class="form-control me-2" type="search" aria-label="Buscar">
      <button class="btn btn-outline-light" type="submit">🔍</button>
    </form>
    </ul>
    
  </div>

        <div class="d-flex align-items-center">
            <a href="carrito.php" class="btn btn-outline-secondary position-relative me-3">
                <i class="fas fa-shopping-cart"></i>
                <?php if ($totalItems > 0): ?>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                        <?= $totalItems ?>
                    </span>
                <?php endif; ?>
            </a>

            <?php if (isset($_SESSION['usuario'])): ?>
                <span class="me-2 d-flex align-items-center text-dark fw-bold">
                    <i class="fas fa-user-circle me-1"></i> <?= htmlspecialchars($_SESSION['usuario']['nombre']) ?>
                </span>
                <a href="logout.php" class="btn btn-danger"><i class="fas fa-sign-out-alt"></i> Cerrar Sesión</a>
            <?php else: ?>
                <a href="AUTH.php" class="btn btn-primary"><i class="fas fa-sign-in-alt"></i> Iniciar Sesión</a>
            <?php endif; ?>
        </div>
</nav>