#include <Arduino.h>
#include <Preferences.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ── BLE provisioning UUIDs ────────────────────────────────────────────────────
#define PROV_SERVICE_UUID  "12345678-1234-5678-1234-56789abcdef0"
#define PROV_CRED_UUID     "12345678-1234-5678-1234-56789abcdef1"
#define PROV_STATUS_UUID   "12345678-1234-5678-1234-56789abcdef2"

// ── WiFi credentials – geladen uit NVS na BLE provisioning ────────────────────
Preferences   preferences;
static String savedSsid;
static String savedPassword;

// ── BLE provisioning state ────────────────────────────────────────────────────
bool                    bleProvisioningActive = false;
static volatile bool    credentialsReceived   = false;
static String           receivedSsid;
static String           receivedPassword;
BLECharacteristic*      pStatusChar = nullptr;

class CredentialCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* pChar) override {
    std::string v   = pChar->getValue();
    String      val = String(v.c_str());
    int         sep = val.indexOf('|');
    if (sep > 0) {
      receivedSsid     = val.substring(0, sep);
      receivedPassword = val.substring(sep + 1);
      credentialsReceived = true;
    }
  }
};

// ── OLED (I2C: SDA=21, SCL=22 op ESP32) ──────────────────────────────────────
#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT  64
#define OLED_RESET     -1
#define OLED_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ── Mutex: beschermt I2C-bus tegen gelijktijdige toegang ─────────────────────
SemaphoreHandle_t i2cMutex = nullptr;

WebServer server(80);

// ── RGB status LED ───────────────────────────────────────────────────────────
// Pas deze pins aan naar jouw bekabeling.
constexpr uint8_t RGB_PIN_R = 25;
constexpr uint8_t RGB_PIN_G = 26;
constexpr uint8_t RGB_PIN_B = 27;
constexpr uint8_t CONNECT_BUTTON_PIN = 33;
// Zet op false voor common-anode RGB LED.
constexpr bool RGB_LED_ACTIVE_HIGH = true;
// Meeste knopbedrading met INPUT_PULLUP is active-low (knop naar GND).
constexpr bool CONNECT_BUTTON_ACTIVE_LOW = true;

enum class LedState {
  Connecting,
  NotConnected,
  Connected,
};

int   temperature = 20;
int   speed_rpm   = 1000;
int   energy      = 50;
float voltage     = 0.0f;
float current_amp = 0.0f;
unsigned long lastDashboardRequestMs = 0;

constexpr unsigned long DASHBOARD_CONNECTION_TIMEOUT_MS = 10000;
constexpr unsigned long CONNECT_BUTTON_DEBOUNCE_MS = 250;

// Simuleer machinespanning: 230V nominaal met kleine drift (EN 50160 norm: 220-240V).
static float voltSmooth = 230.0f;
float readVoltage() {
  float delta = (random(-20, 21)) / 10.0f;  // -2.0 tot +2.0 V per stap
  voltSmooth += delta;
  voltSmooth = constrain(voltSmooth, 220.0f, 240.0f);
  return roundf(voltSmooth * 10.0f) / 10.0f;  // 1 decimaal
}

bool isDashboardConnected() {
  return lastDashboardRequestMs > 0 && (millis() - lastDashboardRequestMs) <= DASHBOARD_CONNECTION_TIMEOUT_MS;
}

void setRgbColor(bool redOn, bool greenOn, bool blueOn) {
  const uint8_t onLevel  = RGB_LED_ACTIVE_HIGH ? HIGH : LOW;
  const uint8_t offLevel = RGB_LED_ACTIVE_HIGH ? LOW : HIGH;

  digitalWrite(RGB_PIN_R, redOn ? onLevel : offLevel);
  digitalWrite(RGB_PIN_G, greenOn ? onLevel : offLevel);
  digitalWrite(RGB_PIN_B, blueOn ? onLevel : offLevel);
}

void setLedState(LedState state) {
  switch (state) {
    case LedState::Connecting:
      setRgbColor(false, false, true);   // blauw
      break;
    case LedState::NotConnected:
      setRgbColor(true, false, false);   // rood
      break;
    case LedState::Connected:
      setRgbColor(false, true, false);   // groen
      break;
  }
}

bool isConnectButtonPressed() {
  const int level = digitalRead(CONNECT_BUTTON_PIN);
  return CONNECT_BUTTON_ACTIVE_LOW ? (level == LOW) : (level == HIGH);
}

// ── BLE provisioning OLED scherm ─────────────────────────────────────────────
void showBleProvisioningScreen() {
  if (i2cMutex && xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(200)) == pdTRUE) {
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print("Machine Monitor");
    display.drawLine(0, 10, SCREEN_WIDTH - 1, 10, SSD1306_WHITE);
    display.setCursor(0, 16);
    display.print("Eerste gebruik!");
    display.setCursor(0, 28);
    display.print("BT actief:");
    display.setCursor(0, 40);
    display.setTextSize(1);
    display.print("MM_PROV");
    display.setCursor(0, 54);
    display.print("Verbind via site");
    display.display();
    xSemaphoreGive(i2cMutex);
  }
}

void startBleProvisioning() {
  Serial.println("[BLE] Provisioning starten als MM_PROV");
  BLEDevice::init("MM_PROV");
  BLEServer*  pServer  = BLEDevice::createServer();
  BLEService* pService = pServer->createService(PROV_SERVICE_UUID);

  // Write characteristic – site schrijft "SSID|WACHTWOORD" hiernaartoe
  BLECharacteristic* pCredChar = pService->createCharacteristic(
    PROV_CRED_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );
  pCredChar->setCallbacks(new CredentialCallbacks());

  // Notify characteristic – ESP32 stuurt "OK:<ip>" of "ERR:..." terug
  pStatusChar = pService->createCharacteristic(
    PROV_STATUS_UUID,
    BLECharacteristic::PROPERTY_NOTIFY
  );
  pStatusChar->addDescriptor(new BLE2902());

  pService->start();

  BLEAdvertising* pAdv = BLEDevice::getAdvertising();
  pAdv->addServiceUUID(PROV_SERVICE_UUID);
  pAdv->setScanResponse(true);
  pAdv->setMinPreferred(0x06);
  BLEDevice::startAdvertising();
  Serial.println("[BLE] Adverteren gestart – wachten op credentials");
}

// ── BLE reset via knop ───────────────────────────────────────────────────────
void resetToBleProv() {
  Serial.println("[BTN] Reset naar BLE provisioning");
  setLedState(LedState::Connecting);  // blauw
  if (i2cMutex && xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(200)) == pdTRUE) {
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print("Machine Monitor");
    display.drawLine(0, 10, SCREEN_WIDTH - 1, 10, SSD1306_WHITE);
    display.setTextSize(2);
    display.setCursor(0, 20);
    display.print("BT modus");
    display.setTextSize(1);
    display.setCursor(0, 50);
    display.print("Herstart...");
    display.display();
    xSemaphoreGive(i2cMutex);
  }
  delay(1500);
  preferences.begin("mm", false);
  preferences.putBool("provisioned", false);
  preferences.end();
  ESP.restart();
}

void updateDisplay() {
  // Wacht maximaal 200 ms op de mutex; sla over als de bus bezet is
  if (i2cMutex && xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(200)) == pdTRUE) {
    display.clearDisplay();

    // ── Header ──
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.print("Machine Monitor");
    display.drawLine(0, 10, SCREEN_WIDTH - 1, 10, SSD1306_WHITE);

    if (!isDashboardConnected()) {
      display.setTextSize(1);
      display.setCursor(0, 18);
      display.print("Site niet");
      display.setCursor(0, 30);
      display.print("verbonden.");
      display.setCursor(0, 46);
      display.print("Open dashboard");
      display.setCursor(0, 56);
      display.print("om te koppelen");
    } else {
      // ── Stroom (groot) ──
      display.setCursor(0, 14);
      display.setTextSize(1);
      display.print("Stroom:");
      display.setTextSize(2);
      display.setCursor(0, 24);
      display.print(current_amp, 2);
      display.print(" A");

      // ── Overige waarden (klein) ──
      display.setTextSize(1);
      display.setCursor(0, 46);
      display.print("Temp: ");
      display.print(temperature);
      display.print(" C");

      display.setCursor(0, 56);
      display.print("RPM: ");
      display.print(speed_rpm);
    }

    display.display();
    xSemaphoreGive(i2cMutex);
  }
}

void handleData() {
  lastDashboardRequestMs = millis();

  // Simulatie voor temperature, speed en energy
  temperature += random(-1, 2);
  speed_rpm   += random(-50, 50);
  energy      += random(-5, 5);

  temperature = constrain(temperature, 15, 80);
  speed_rpm   = constrain(speed_rpm, 500, 3000);
  energy      = constrain(energy, 10, 200);

  // Voltage blijft beschikbaar voor API, stroom op scherm volgt dashboard-logica
  voltage = readVoltage();
  current_amp = constrain(energy / 40.0f, 0.5f, 6.0f);

  // Scherm wordt bijgewerkt vanuit loop() – niet hier, om I2C-conflicten te voorkomen

  String json = "{";
  json += "\"temperature\":" + String(temperature) + ",";
  json += "\"speed\":"       + String(speed_rpm)   + ",";
  json += "\"energy\":"      + String(energy)       + ",";
  json += "\"current\":"     + String(current_amp, 2) + ",";
  json += "\"voltage\":"     + String(voltage, 2);
  json += "}";

  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);

  pinMode(RGB_PIN_R, OUTPUT);
  pinMode(RGB_PIN_G, OUTPUT);
  pinMode(RGB_PIN_B, OUTPUT);
  if (CONNECT_BUTTON_ACTIVE_LOW) {
    pinMode(CONNECT_BUTTON_PIN, INPUT_PULLUP);
  } else {
    pinMode(CONNECT_BUTTON_PIN, INPUT_PULLDOWN);
  }
  setLedState(LedState::Connecting);

  // ── Mutex aanmaken vóór alles ──
  i2cMutex = xSemaphoreCreateMutex();

  // ── OLED init ──
  Wire.begin();
  Wire.setClock(100000);  // 100 kHz – stabieler bij WiFi + BLE
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS)) {
    Serial.println("SSD1306 niet gevonden – controleer bedrading!");
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.print("Booting...");
    display.display();
  }

  // ── NVS / provisioning check ──────────────────────────────────────────────
  preferences.begin("mm", false);
  bool isProvisioned = preferences.getBool("provisioned", false);

  if (!isProvisioned) {
    // Eerste gebruik: credentials ontbreken → BLE provisioning starten
    preferences.end();
    bleProvisioningActive = true;
    setLedState(LedState::Connecting);  // blauw
    showBleProvisioningScreen();
    startBleProvisioning();
    return;  // loop() handelt de provisioning af
  }

  // Laad WiFi credentials uit NVS
  savedSsid     = preferences.getString("ssid", "");
  savedPassword = preferences.getString("password", "");
  preferences.end();

  // ── WiFi ──
  WiFi.begin(savedSsid.c_str(), savedPassword.c_str());
  Serial.print("Verbinden met WiFi");;
  while (WiFi.status() != WL_CONNECTED) {
    setLedState(LedState::Connecting);
    delay(500);
    Serial.print(".");
  }

  setLedState(LedState::NotConnected);

  Serial.println("\nVerbonden!");
  Serial.println(WiFi.localIP());
  Serial.print("Data endpoint: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/data");

  // Toon eerst het IP, daarna wacht-scherm tot de site verbindt
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("WiFi OK!");
  display.setCursor(0, 12);
  display.print(WiFi.localIP());
  display.display();
  delay(2000);

  server.on("/data", handleData);
  server.begin();
  Serial.print("Data endpoint: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/data");

  // Eerste schermupdates
  voltage = readVoltage();
  current_amp = constrain(energy / 40.0f, 0.5f, 6.0f);
  updateDisplay();
}

void loop() {
  // ── BLE provisioning modus ────────────────────────────────────────────────
  if (bleProvisioningActive) {
    if (credentialsReceived) {
      Serial.println("[BLE] Credentials ontvangen – opslaan in NVS");
      preferences.begin("mm", false);
      preferences.putBool("provisioned", true);
      preferences.putString("ssid", receivedSsid);
      preferences.putString("password", receivedPassword);
      preferences.end();

      // Verbinden met het opgegeven WiFi-netwerk
      WiFi.begin(receivedSsid.c_str(), receivedPassword.c_str());
      Serial.print("[BLE] Verbinden met WiFi");
      unsigned long wifiStart = millis();
      while (WiFi.status() != WL_CONNECTED && millis() - wifiStart < 15000) {
        delay(300);
        Serial.print(".");
      }

      if (WiFi.status() == WL_CONNECTED) {
        String ip = WiFi.localIP().toString();
        Serial.println("\n[BLE] WiFi OK – IP: " + ip);
        if (pStatusChar) {
          String msg = "OK:" + ip;
          pStatusChar->setValue(msg.c_str());
          pStatusChar->notify();
        }
      } else {
        Serial.println("\n[BLE] WiFi verbinding mislukt");
        if (pStatusChar) {
          pStatusChar->setValue("ERR:WiFi verbinding mislukt");
          pStatusChar->notify();
        }
        // Verwijder opgeslagen credentials zodat provisioning opnieuw start
        preferences.begin("mm", false);
        preferences.putBool("provisioned", false);
        preferences.end();
      }

      delay(1500);  // geef BLE notificatie tijd om te verzenden
      ESP.restart();
    }

    // LED blauw knipperen tijdens wachten op provisioning
    static unsigned long lastBlink  = 0;
    static bool          blinkState = false;
    if (millis() - lastBlink > 600) {
      lastBlink  = millis();
      blinkState = !blinkState;
      setRgbColor(false, false, blinkState);  // blauw knipperen
    }
    return;  // normale loop-code overslaan
  }

  server.handleClient();

  static bool lastRawPressed = false;
  static bool stablePressed = false;
  static unsigned long rawChangedAtMs = 0;

  const bool rawPressed = isConnectButtonPressed();
  if (rawPressed != lastRawPressed) {
    lastRawPressed = rawPressed;
    rawChangedAtMs = millis();
  }

  if ((millis() - rawChangedAtMs) >= CONNECT_BUTTON_DEBOUNCE_MS && rawPressed != stablePressed) {
    stablePressed = rawPressed;
    if (stablePressed) {
      Serial.println("[BTN] Reset naar BLE provisioning");
      resetToBleProv();  // nooit terug – ESP herstart
    }
  }

  if (WiFi.status() != WL_CONNECTED) {
    setLedState(LedState::Connecting);
  } else if (isDashboardConnected()) {
    setLedState(LedState::Connected);
  } else {
    setLedState(LedState::NotConnected);
  }

  // ── Scherm elke 1000 ms vernieuwen ──
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 1000) {
    voltage = readVoltage();
    current_amp = constrain(energy / 40.0f, 0.5f, 6.0f);
    updateDisplay();
    lastUpdate = millis();
  }
}