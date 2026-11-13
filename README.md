# Banco API — Escaneo de vulnerabilidades con DevSkim y Grype

Proyecto grupal del curso **Calidad y Pruebas de Software (UPT)**. Integra dos herramientas de la
[lista de herramientas de escaneo de vulnerabilidades de OWASP](https://owasp.org/www-community/Vulnerability_Scanning_Tools)
en un pipeline automatizado con GitHub Actions:

| Herramienta | Tipo | Qué revisa | Responsable |
| --- | --- | --- | --- |
| [DevSkim](https://github.com/microsoft/DevSkim) | SAST | Código fuente C# | Victor Carretero |
| [Grype](https://github.com/anchore/grype) | SCA | Paquetes NuGet e imagen Docker | Gerald Deybi Zevallos Pinto |

> ⚠️ La aplicación contiene vulnerabilidades **intencionales** (hash MD5/SHA1, credenciales en el código,
> generador aleatorio inseguro, URL HTTP y `Newtonsoft.Json 12.0.1` con CVE conocido). No usar en producción.

## Pipeline

El workflow [`seguridad.yml`](.github/workflows/seguridad.yml) se ejecuta en cada `push` o `pull request` a `main`:

```
push → build (.NET 8) ─┬→ DevSkim (código)          ─┐
                       └→ Docker build → Grype (SCA) ─┴→ GitHub Code Scanning + reportes HTML → GitHub Pages
```

1. Compila la API .NET 8.
2. **DevSkim** escanea el código fuente y genera un SARIF.
3. Se construye la imagen Docker y **Grype** la escanea en busca de CVE.
4. Ambos resultados se suben a **Security → Code scanning**.
5. Se generan reportes HTML y se publican en **GitHub Pages**.

## Reportes publicados

https://viccarretero.github.io/banco-api-vulnerabilidades/

## Ejecutar en local

```bash
# DevSkim
dotnet tool install --global Microsoft.CST.DevSkim.CLI
devskim analyze --source-code src --output-file devskim.sarif

# Grype
docker build -t banco-api .
grype banco-api

# Aplicación
dotnet run --project src/BancoApi
```

## Configuración del repositorio

En **Settings → Pages**, seleccionar **Source: GitHub Actions**.

## Integrantes

- Victor Carretero
- Gerald Deybi Zevallos Pinto
