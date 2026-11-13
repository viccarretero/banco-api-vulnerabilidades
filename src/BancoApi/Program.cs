using System.Security.Cryptography;
using System.Text;

// =====================================================================
// Banco API - aplicación de demostración para escaneo con DevSkim.
// ATENCIÓN: este código contiene vulnerabilidades INTENCIONALES para
// que DevSkim las detecte. No usar en producción.
// =====================================================================

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// [Vulnerable] Credenciales escritas directamente en el código
const string ConnectionString = "Server=db.banco.local;User Id=admin;Password=Admin123!;";

var cuentas = new Dictionary<string, decimal>
{
    ["001"] = 1500m,
    ["002"] = 320.50m,
    ["003"] = 9800m
};

app.MapGet("/", () => "Banco API - demo de escaneo de vulnerabilidades con DevSkim");

app.MapGet("/cuentas/{id}", (string id) =>
    cuentas.TryGetValue(id, out var saldo)
        ? Results.Ok(new { id, saldo })
        : Results.NotFound());

// [Vulnerable] Algoritmo de hash débil (MD5)
app.MapGet("/hash/{texto}", (string texto) =>
{
    using var md5 = MD5.Create();
    var hash = md5.ComputeHash(Encoding.UTF8.GetBytes(texto));
    return Convert.ToHexString(hash);
});

// [Vulnerable] Algoritmo de hash débil (SHA1)
app.MapGet("/firma/{texto}", (string texto) =>
{
    using var sha1 = SHA1.Create();
    var hash = sha1.ComputeHash(Encoding.UTF8.GetBytes(texto));
    return Convert.ToHexString(hash);
});

// [Vulnerable] Generador aleatorio no criptográfico para tokens
app.MapGet("/token", () =>
{
    var random = new Random();
    return random.Next(100000, 999999).ToString();
});

// [Vulnerable] Comunicación sin cifrar (HTTP)
app.MapGet("/tipo-cambio", () => Results.Redirect("http://api.tipocambio.example.com/usd"));

// [Vulnerable] Usa una librería con vulnerabilidad conocida (Newtonsoft.Json 12.0.1)
app.MapGet("/exportar", () =>
    Results.Text(Newtonsoft.Json.JsonConvert.SerializeObject(cuentas), "application/json"));

// TODO: mover la cadena de conexión a variables de entorno
app.MapGet("/config", () => Results.Ok(new { configurado = ConnectionString.Length > 0 }));

app.Run();

public partial class Program { }
