import time
import requests
import Adafruit_DHT
import RPi.GPIO as GPIO

# Configurações dos pinos e sensores
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # Pino de leitura do sensor DHT22
RELAY_PIN = 17  # Pino de controle do relé para o ar-condicionado
PIR_PIN = 27   # Pino de entrada do sensor de movimento

# Configuração da API do ThingSpeak
THINGSPEAK_WRITE_API_KEY = 'OWN3GD01HAE06PS2'
THINGSPEAK_CHANNEL_ID = '2643920'

# Variável para armazenar o tempo da última detecção de movimento
last_motion_time = time.time()

# Função para enviar dados para o ThingSpeak
def send_to_thingspeak(temperature, humidity, energy_consumption):
    url = f"https://api.thingspeak.com/update?api_key=OWN3GD01HAE06PS2&field1=0"
    payload = {
        'field1': temperature,
        'field2': humidity,
        'field3': energy_consumption
    }
    response = requests.get(url, params=payload)
    return response.status_code

# Função para controlar o relé do ar-condicionado
def control_ac(state):
    GPIO.output(RELAY_PIN, state)

# Configuração dos pinos GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(PIR_PIN, GPIO.IN)

try:
    while True:
        # Leitura dos dados do sensor DHT22
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        
        if humidity is not None and temperature is not None:
            energy_consumption = temperature * 0.5  
            
            # Envia os dados para o ThingSpeak
            status = send_to_thingspeak(temperature, humidity, energy_consumption)
            
            if status == 200:
                print("Dados enviados com sucesso para o ThingSpeak.")
            else:
                print(f"Falha ao enviar os dados: {status}")
            
            # Desligar o ar-condicionado se não houver movimento por mais de 5 minutos
            motion_detected = GPIO.input(PIR_PIN)
            
            if motion_detected:
                last_motion_time = time.time()
                control_ac(GPIO.HIGH)
                print("Movimento detectado. Ar-condicionado ligado.")
            elif time.time() - last_motion_time > 300:  # 300 segundos = 5 minutos
                control_ac(GPIO.LOW)
                print("Nenhum movimento detectado por mais de 5 minutos. Ar-condicionado desligado.")
            else:
                print("Aguardando mais detecção de movimento.")
            
        else:
            print("Falha ao ler os dados do sensor DHT22.")
        
        # Intervalo entre as leituras
        time.sleep(10)  # Ajuste o tempo conforme necessário

except KeyboardInterrupt:
    print("Encerrando o programa.")

finally:
    GPIO.cleanup()
