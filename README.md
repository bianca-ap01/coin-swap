
# Proyecto Coin Swap

Proyecto backend con FastAPI para simulación de conversión y transferencia de monedas entre usuarios, usando PostgreSQL y MongoDB.

---

## Características

- Registro y autenticación de usuarios sin contraseña (solo por nombre de usuario).
- Transferencias entre usuarios en las monedas PEN y USD.
- Conversión de monedas (PEN ↔ USD).
- Gestión de saldos con operaciones de depósito y retiro.
- Historial de transacciones.
- Soporte para múltiples proveedores de tasas de cambio.

---

## Requisitos

- **Python 3.9+**
- **PostgreSQL** para la base de datos.
- **MongoDB** para el almacenamiento de las transacciones.
- **Docker** (opcional, para facilitar la configuración de las bases de datos).

---

## Configuración y ejecución

1. Clonar el repositorio:

```bash
git clone https://github.com/bianca-ap01/coin-swap.git
cd coin-swap
```

2. Crear y activar entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# o en Windows
venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Levantar bases de datos con Docker Compose (Opcional):

```bash
docker-compose up -d
```

Esto levantará dos contenedores: PostgreSQL (5432) y MongoDB (27017).

5. Crear las tablas:

```bash
uvicorn app.main:app --reload
```

Esto iniciará FastAPI y ejecutará las migraciones automáticamente.

Usuarios por defecto:
- Usuario X: `S/. 100`, `USD 200`
- Usuario Y: `S/. 50`, `USD 100`

6. Visualizar la aplicación:

```bash
cd frontend/
start index.html # Windows
# o
xdg-open index.html # Linux/macOS
```

---

## Endpoints API

### 1. Registrar nuevo usuario

```http
POST /auth/register/
```

### 2. Obtener token de acceso

```http
POST /auth/token/
```

### 3. Consultar saldo

```http
GET /users/me/balance/
```

### 4. Realizar transferencia

```http
POST /transfer/transfer/
```

### 5. Convertir monedas

```http
POST /transfer/convert/
```

### 6. Depósito o Retiro

```http
POST /transfer/user/balance/change/
```

### 7. Ver historial de transacciones

```http
GET /transactions/
```

---

## Patrones de diseño

- **Singleton**: en `CurrencyAPIClientSingleton` para una sola instancia de cliente de API.
- **Adapter**: integración flexible con múltiples fuentes de tasas de cambio.

---

## Estructura del repositorio

```bash
coin-swap/
├── app/
│   ├── api/
│   ├── core/
│   ├── crud/
│   ├── models/
│   └── main.py
├── frontend/
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---



# EC4 - Pruebas Unitarias y Performance API Monedas

## Grupo e Integrantes

- Bianca Aguinaga  
- Zamir Lizardo  
- Jorge Melgarejo  
- Ariana Mercado  
- Matías Meneses  
- Badi Rodríguez  

---

## Pruebas Unitarias

- Realizadas con `PyTest` o `UnitTest`.
- Reporte de Code Coverage: **100% en servicios** (excluye routers/controladores).
- Pruebas enfocadas exclusivamente en **métodos o servicios**, **no en endpoints**.

### Buenas prácticas

- Mocks de `httpx.AsyncClient`, JWT y BD.
- Verificación de excepciones con `pytest.raises`.
- Asserts de interacción: `await_count`, `assert_called_once_with`.

---

## ⚙️ Stack de Test

| Herramienta         | Uso                                                        |
|---------------------|------------------------------------------------------------|
| PyTest              | Framework de testing síncrono y asíncrono                 |
| Coverage.py         | Medición de cobertura de líneas y ramas                   |
| unittest.mock       | Aislamiento de dependencias (HTTP, BD, JWT, etc.)         |
| pytest-asyncio      | Soporte para coroutines en pruebas `async`                |

---

## Cobertura Alcanzada

| Módulo                      | Líneas | Cubiertas | %     |
|----------------------------|--------|-----------|-------|
| `currency_client.py`       | 185    | 185       | 100%  |
| `security.py`              | 142    | 142       | 100%  |
| `transaction.py`           | 68     | 68        | 100%  |
| `user.py`                  | 57     | 57        | 100%  |
| **TOTAL servicios**        | **452**| **452**   |**100%**|

![Resultados de Code Coverage](attachment:image.png)

---

## Resumen de Casos por Archivo

| Archivo                        | Casos clave cubiertos                                                                 |
|-------------------------------|----------------------------------------------------------------------------------------|
| `test_core_currency_client.py`| Éxitos y errores en API; Singleton; cambio de adaptador dinámico                      |
| `test_core_security.py`       | JWT con expiración; payload extendido; flujo `get_current_user` y errores relacionados|
| `test_crud_transaction.py`    | Inserción asíncrona; consulta paginada                                               |
| `test_crud_user.py`           | Búsqueda, creación con saldos, persistencia de cambios                                |

---

## Autenticación y Seguridad

- Pruebas para tokens JWT válidos, expirados e inválidos.
- Control total sobre las dependencias `Depends` de FastAPI para evitar problemas de inyección.

---

## Estructura de Archivos de Test

Organización por módulo:

```
test_crud_user.py
test_crud_transaction.py
test_core_currency_client.py
test_core_security.py
```

---

## Pruebas de Performance

- Herramienta sugerida: **JMeter** (o similar).
- No usar API real → usar **mock** o **modo caché** que simule un delay de **500ms**.

### Escenario propuesto

1. Depósito y transferencia.
2. Transferencias de ida y vuelta entre monedas distintas.
3. Validar que el estado final de la BD sea **consistente** (saldos coherentes).

---

## Entregables

- Archivo `.jmx` u equivalente.
- Capturas de pantalla como evidencia.
- Informe y código disponible en el repositorio:

🔗 [Repositorio en GitHub](https://github.com/bianca-ap01/coin-swap)

🔗 [Rama: badi-flicks (Performance)](https://github.com/bianca-ap01/coin-swap/tree/badi-flicks)
