call C:\Users\Android\Desktop\mos\LSP\lsp\Scripts\activate
cd C:\Users\Android\Desktop\mos\LSP

echo        Run MQTT Broker
pause
start cmd /k "mosquitto -v -c broker.conf"

echo        Run Flask Web Server
pause
start cmd /k "python WebServer.py"

echo        Run SystemController.py
pause
start cmd /k "python SystemController.py"


