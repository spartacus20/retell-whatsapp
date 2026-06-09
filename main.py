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

SIP_DOMAIN = "5t4n6j0wnrl.sip.livekit.cloud"

# Validar configuración
if not RETELL_API_KEY:
    raise ValueError("RETELL_API_KEY no está configurado en las variables de entorno")
if not RETELL_AGENT_ID:
    raise ValueError("RETELL_AGENT_ID no está configurado en las variables de entorno")

logger.info(f"Configuración cargada - Agent ID: {RETELL_AGENT_ID}")

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

@app.post("/new-call/{agent_id}")
async def new_call_by_agent(agent_id: str, request: Request):
    """Maneja llamadas entrantes de Twilio e inicia llamadas Retell usando un agent_id de la ruta."""
    form_data = await request.form()
    
    call_sid = form_data.get('CallSid')
    from_number = form_data.get('From')
    to_number = form_data.get('To')
    
    logger.info(f"new-call-by-agent: Agent ID: {agent_id}, Call SID: {call_sid}, From: {from_number}, To: {to_number}")
    
    try:
        sip_endpoint = f"{agent_id}@verbeo-ai.sip.twilio.com"
        logger.info(f"new-call-by-agent: Dialing SIP endpoint: {sip_endpoint}")
        
        voice_response = VoiceResponse()
        voice_response.dial().sip(sip_endpoint)
        
        return Response(
            content=str(voice_response),
            media_type="application/xml",
            headers={"Content-Type": "application/xml"}
        )
        
    except Exception as e:
        logger.error(f"new-call-by-agent: Error: {e}, type: {type(e)}")
        voice_response = VoiceResponse()
        voice_response.say("Sorry, there was an error connecting.")
        
        return Response(
            content=str(voice_response),
            media_type="application/xml",
            headers={"Content-Type": "application/xml"}
        )

@app.get("/asterisk-new-call")
async def asterisk_new_call(from_number: str, to_number: str):
    """Endpoint para Asterisk: registra la llamada en Retell y devuelve el call_id en texto plano."""
    logger.info(f"asterisk-new-call: From: {from_number}, To: {to_number}")
    try:
        retell_call_response = retell_client.call.register_phone_call(
            agent_id=RETELL_AGENT_ID,
            from_number=from_number,
            to_number=to_number,
            direction="inbound"
        )
        call_id = retell_call_response.call_id
        logger.info(f"asterisk-new-call: call_id registrado: {call_id}")
        # Devolvemos SOLO el call_id, sin JSON, para que Asterisk lo lea directo
        return Response(content=call_id, media_type="text/plain")
    except Exception as e:
        logger.error(f"asterisk-new-call: Error: {e}")
        # Devolver vacío para que el dialplan detecte el fallo
        return Response(content="", media_type="text/plain", status_code=500)



# Almacenamiento de datos de llamadas (necesario para el endpoint new-call)
call_data_store = {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 