from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from retell import Retell
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp SIP Redirect API con Retell", version="1.0.0")

# Configuración directa
RETELL_API_KEY = os.environ.get('RETELL_API_KEY')
RETELL_AGENT_ID = os.environ.get('RETELL_AGENT_ID')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER')
SIP_DOMAIN = "5t4n6j0wnrl.sip.livekit.cloud"

# Validar configuración
if not RETELL_API_KEY:
    raise ValueError("RETELL_API_KEY no está configurado en las variables de entorno")
if not RETELL_AGENT_ID:
    raise ValueError("RETELL_AGENT_ID no está configurado en las variables de entorno")
if not PHONE_NUMBER:
    raise ValueError("PHONE_NUMBER no está configurado en las variables de entorno")

logger.info(f"Configuración cargada - Agent ID: {RETELL_AGENT_ID}, Phone: {PHONE_NUMBER}")

# Inicializar cliente Retell
retell_client = Retell(api_key=RETELL_API_KEY)

@app.post("/new-call")
async def new_call(request: Request):
    """Maneja llamadas entrantes de Twilio e inicia llamadas Retell."""
    form_data = await request.form()
    
    call_sid = form_data.get('CallSid')
    from_number = form_data.get('From')
    to_number = form_data.get('To')
    
    logger.info(f"new-call: Call SID: {call_sid}, From: {from_number}, To: {to_number}")
    
    try:
        # Si es una llamada saliente (from_number == PHONE_NUMBER), buscamos el retell_call_id en el call_data_store
        # Si es una llamada entrante, registramos una nueva llamada con Retell
        if from_number == PHONE_NUMBER:
            # Para llamadas salientes, el retell_call_id ya debería estar en call_data_store
            if to_number in call_data_store and 'retell_call_id' in call_data_store[to_number]:
                retell_call_id = call_data_store[to_number]['retell_call_id']
                logger.info(f"new-call: Usando retell_call_id existente: {retell_call_id}")
            else:
                # Si por algún motivo no está registrado, lo registramos ahora
                retell_call_response = retell_client.call.register_phone_call(
                    agent_id=RETELL_AGENT_ID,
                    from_number=from_number,
                    to_number=to_number,
                    direction="outbound",
                    retell_llm_dynamic_variables=form_data.get('retell_llm_dynamic_variables', {})
                )
                retell_call_id = retell_call_response.call_id
                call_data_store[to_number] = {
                    'call_sid': call_sid,
                    'retell_call_id': retell_call_id
                }
                logger.info(f"new-call: Registrada nueva llamada saliente con Retell: {retell_call_id}")
        else:
            # Para llamadas entrantes, siempre registramos una nueva llamada con Retell
            retell_call_response = retell_client.call.register_phone_call(
                agent_id=RETELL_AGENT_ID,
                from_number=from_number,
                to_number=to_number,
                direction="inbound"
            )
            retell_call_id = retell_call_response.call_id
            call_data_store[from_number] = {
                'call_sid': call_sid,
                'retell_call_id': retell_call_id
            }
            logger.info(f"new-call: Registrada nueva llamada entrante con Retell: {retell_call_id}")
        
        sip_endpoint = f"sip:{retell_call_id}@{SIP_DOMAIN}"
        logger.info(f"new-call: Dialing SIP endpoint: {sip_endpoint}")
        
        voice_response = VoiceResponse()
        voice_response.dial().sip(sip_endpoint)
        
        return Response(
            content=str(voice_response),
            media_type="application/xml",
            headers={"Content-Type": "application/xml"}
        )
        
    except Exception as e:
        logger.error(f"new-call: Error: {e}, type: {type(e)}")
        voice_response = VoiceResponse()
        voice_response.say("Sorry, there was an error connecting.")
        
        return Response(
            content=str(voice_response),
            media_type="application/xml",
            headers={"Content-Type": "application/xml"}
        )

# Almacenamiento de datos de llamadas (necesario para el endpoint new-call)
call_data_store = {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 