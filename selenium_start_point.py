from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import traceback
import random

JS_INTERCEPTOR = """
(function() {
    if (window.requestInterceptorInitialized) {
        return;
    }
    window.requestInterceptorInitialized = true;
    console.log("JS Interceptor: Initializing...");

    window.interceptedRequests = window.interceptedRequests || [];

    const originalXhrOpen = XMLHttpRequest.prototype.open;
    const originalXhrSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._requestMethod = method;
        this._requestUrl = url;
        originalXhrOpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function(body) {
        if (this._requestUrl && this._requestUrl.includes('service/conferencesession') && this._requestMethod === 'POST') {
            console.log(`JS Interceptor: Intercepted XHR Send - ${this._requestMethod} ${this._requestUrl}`);
            try {
                const requestData = {
                    type: 'XHR',
                    method: this._requestMethod,
                    url: this._requestUrl,
                    postData: body
                };
                window.interceptedRequests.push(requestData);
                console.log("JS Interceptor: XHR Request data captured.", requestData);
            } catch (e) {
                console.error("JS Interceptor: Error capturing XHR data:", e);
                window.interceptedRequests.push({ type: 'XHR', error: 'Capture failed', url: this._requestUrl });
            }
        }
        originalXhrSend.apply(this, arguments);
    };

    const originalFetch = window.fetch;
    window.fetch = function(input, init) {
        let url;
        let method = 'GET';
        let requestBody = null;

        if (typeof input === 'string') {
            url = input;
        } else if (input instanceof Request) {
            url = input.url;
            method = input.method || 'GET';
        } else {
            url = input ? input.toString() : 'unknown';
        }

        if (init) {
            method = init.method || method;
            requestBody = init.body;
        }

        if (url && url.includes('service/conferencesession') && method === 'POST') {
            console.log(`JS Interceptor: Intercepted Fetch - ${method} ${url}`);
            try {
                const requestData = {
                    type: 'Fetch',
                    method: method,
                    url: url,
                    postData: requestBody ? String(requestBody) : null
                };
                window.interceptedRequests.push(requestData);
                console.log("JS Interceptor: Fetch Request data captured:", requestData);
            } catch (e) {
                console.error("JS Interceptor: Error capturing Fetch data:", e);
                window.interceptedRequests.push({ type: 'Fetch', error: 'Capture failed', url: url });
            }
        }

        return originalFetch.apply(this, arguments);
    };

    console.log("JS Interceptor: Initialized successfully.");
})();
"""


def initialize_driver():
    print("Инициализация WebDriver...")
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_driver_path = r"chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("WebDriver инициализирован.")
    return driver


def close_driver(driver):
    if driver:
        print("Завершаем работу WebDriver...")
        try:
            driver.quit()
            print("WebDriver завершил работу.")
        except Exception as e:
            print(f"Ошибка при завершении работы WebDriver: {e}")
    else:
        print("WebDriver не был инициализирован или уже закрыт.")


def run_capture_logic():
    init = random.randint(1, 100)
    driver = initialize_driver()
    try:
        url = f"https://e-class.tsu.ru/#join:t453ad5ce-f583-4b79-a9d3-cb52f93c3542,true,test{init}"
        print(f"Открываем страницу: {url}")
        driver.get(url)
        print("Страница открыта.")

        time.sleep(2)

        print("Ожидание элемента с текстом 'любое_имя'...")
        name_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[text()='test{init}']"))
        )

        print("Элемент 'любое_имя' найден. Кликаем...")
        name_element.click()
        print("Клик по элементу 'любое_имя' выполнен.")

        time.sleep(2)

        print("Внедряем JavaScript перехватчик...")
        driver.execute_script(JS_INTERCEPTOR)
        print("JavaScript перехватчик внедрен.")

        time.sleep(2)

        print("Ожидание первой кнопки (метка GBDGNBYD3C)...")
        first_label = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "(//*[@class='gwt-Label GBDGNBYD3C'])[1]")
            )
        )

        time.sleep(0.5)

        first_label.click()
        print("Нажата первая кнопка с классом 'gwt-Label GBDGNBYD3C'")

        second_label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//*[@class='GBDGNBYB3C'])//*[2]"))
        )

        time.sleep(2)

        print("Ожидание поля ввода...")
        text_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//*[@class='GBDGNBYNMB GBDGNBYL3C']//*[@class='mind-textbox-content']",
                )
            )
        )
        time.sleep(2)

        
        text_input.send_keys("test1")
        time.sleep(2)
        
        # time.sleep(2)
        
        second_label.click()
        print("В поле ввода введено: test1")
        print("Нажимаем вторую кнопку (ожидаем перехвата JS)...")

        print("Вторая кнопка нажата.")

        print("Ожидание срабатывания JS перехватчика (несколько секунд)...")
        time.sleep(5)

        print("Извлечение данных из JS переменной window.interceptedRequests...")
        intercepted_data = driver.execute_script("return window.interceptedRequests;")
        print(
            f"Извлечено {len(intercepted_data) if intercepted_data else 0} записей из JS."
        )

        target_request_data = None
        if intercepted_data:
            for req_data in intercepted_data:
                if (
                    req_data
                    and "url" in req_data
                    and "service/conferencesession" in req_data["url"]
                    and req_data.get("method") == "POST"
                ):
                    print(f"Найден целевой запрос в данных JS: {req_data.get('url')}")
                    target_request_data = req_data
                    break

        if target_request_data:
            print("\n--- Перехваченный запрос (JS Injection) ---")

            cookies = driver.get_cookies()
            cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

            save_data = {
                "method": target_request_data.get("method"),
                "url": target_request_data.get("url"),
                "headers": {"Cookie": cookie_string},
                "postData": target_request_data.get("postData"),
                "source_type": target_request_data.get("type"),
            }
            print(json.dumps(save_data, indent=2, ensure_ascii=False))

            try:
                with open("captured_request_js.json", "w", encoding="utf-8") as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                print("\nЗапрос сохранен в captured_request_js.json")
            except IOError as e:
                print(f"\nОшибка сохранения запроса в файл: {e}")
        else:
            print(
                "\nЦелевой POST запрос к 'service/conferencesession' не был найден в данных, перехваченных JS."
            )
            if intercepted_data:
                print("\nВсе перехваченные JS данные:")
                print(json.dumps(intercepted_data, indent=2, ensure_ascii=False))
        return driver

    except Exception as e:
        print(f"\nПроизошла КРИТИЧЕСКАЯ ошибка выполнения скрипта: {e}")
        print("Полная информация об ошибке:")
        traceback.print_exc()


if __name__ == "__main__":
    driver = run_capture_logic()
    time.sleep(500)
    # close_driver(driver)
