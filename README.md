# WhatsApp SIP Redirect API con Retell

Una API simple en FastAPI que maneja llamadas telefónicas con redirección a endpoints SIP de Retell.

## 🚀 Características

- **Integración con Retell**: Agentes de IA para conversaciones telefónicas
- **Redirección SIP**: Conecta llamadas Twilio con endpoints SIP de Retell
- **Manejo de llamadas entrantes y salientes**: Lógica inteligente para ambos tipos de llamadas
- **Logging completo**: Para debugging y monitoreo
- **Dominio SIP configurado**: `5t4n6j0wnrl.sip.livekit.cloud`

## 📋 Endpoint Disponible

- **`POST /new-call`**: Maneja llamadas entrantes de Twilio e inicia llamadas Retell

## 🛠️ Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <tu-repositorio>
   cd Whatsapp
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp env.example .env
   # Editar .env con tus credenciales
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

La API estará disponible en `http://localhost:3000`

## ⚙️ Configuración

### Variables de Entorno Requeridas

```bash
# Retell
RETELL_API_KEY=tu_api_key_de_retell
INBOUND_RETELL_AGENT_ID=agent_id_para_llamadas_entrantes
OUTBOUND_RETELL_AGENT_ID=agent_id_para_llamadas_salientes

# Teléfono
PHONE_NUMBER=+1234567890
```

**Nota**: El dominio SIP está configurado directamente en el código como `5t4n6j0wnrl.sip.livekit.cloud`

## 📱 Uso

### Simular una Llamada Entrante

```bash
curl -X POST "http://localhost:3000/new-call" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=CA1234567890abcdef&From=+1987654321&To=+1234567890"
```

### Simular una Llamada Saliente

```bash
curl -X POST "http://localhost:3000/new-call" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=CA1234567890abcdef&From=+1234567890&To=+1987654321"
```

## 🔄 Flujo de Llamadas

### Llamadas Entrantes
1. **Número entrante** → Twilio recibe la llamada
2. **`POST /new-call`** → Twilio solicita TwiML
3. **Retell** → Registra la llamada y devuelve ID
4. **TwiML** → Redirige a `sip:{retell_call_id}@5t4n6j0wnrl.sip.livekit.cloud`

### Llamadas Salientes
1. **Llamada saliente** → Twilio inicia la llamada
2. **`POST /new-call`** → Twilio solicita TwiML
3. **Retell** → Registra la llamada y devuelve ID
4. **TwiML** → Redirige a `sip:{retell_call_id}@5t4n6j0wnrl.sip.livekit.cloud`

## 📊 Ejemplo de TwiML Generado

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial>
        <Sip>sip:abc123def456@5t4n6j0wnrl.sip.livekit.cloud</Sip>
    </Dial>
</Response>
```

## 🧪 Pruebas

Ejecuta el script de pruebas para verificar la funcionalidad:

```bash
python test_api.py
```

## 📚 Documentación de la API

Una vez que la aplicación esté ejecutándose, puedes acceder a la documentación automática en:
- **Swagger UI**: `http://localhost:3000/docs`
- **ReDoc**: `http://localhost:3000/redoc`

## 🔧 Configuración de Twilio

### Webhook URL
Configura este webhook en tu cuenta de Twilio:

- **Voice Configuration**: `https://tu-url.com/new-call`

### Números de Teléfono
Asegúrate de que tu número de Twilio esté configurado para:
- Llamadas de voz
- Webhooks de voz

## 🌐 Configuración de ngrok

Para desarrollo local, usa ngrok para exponer tu servidor:

```bash
ngrok http 3000
```

## 📝 Notas Importantes

- **Puerto**: La API corre en el puerto 3000
- **Dominio SIP**: Configurado como `5t4n6j0wnrl.sip.livekit.cloud`
- **Logging**: Logging completo para debugging y monitoreo
- **Manejo de Errores**: Manejo robusto de errores con respuestas apropiadas
- **Variables Dinámicas**: Soporte para variables personalizadas de Retell

## 🚨 Solución de Problemas

### Error de Configuración
```bash
python test_api.py
```
Verifica que todas las variables de entorno estén configuradas.

### Error de Dependencias
```bash
pip install -r requirements.txt --upgrade
```

### Puerto en Uso
Cambia el puerto en `main.py` o detén otros servicios que usen el puerto 3000.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. # retell-whatsapp
