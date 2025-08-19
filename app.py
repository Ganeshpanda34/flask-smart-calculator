from flask import Flask, render_template_string, request, jsonify
import math

app = Flask(__name__)

# Store calculation history
history = []

# HTML + CSS + JS in one place
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Powerful Flask Calculator</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      background: linear-gradient(135deg, #1f2937, #111827);
      color: white;
    }

    .calculator-container {
      display: flex;
      gap: 15px;
    }

    .calculator {
      background: #1e293b;
      padding: 20px;
      border-radius: 15px;
      box-shadow: 0 8px 25px rgba(0,0,0,0.4);
      width: 330px;
      max-width: 90vw;
      transition: transform 0.3s ease-in-out;
    }

    .calculator:hover {
      transform: scale(1.02);
    }

    .display {
      width: 100%;
      height: 60px;
      background: #111827;
      border: none;
      border-radius: 10px;
      color: #fff;
      font-size: 22px;
      padding: 10px 20px;
      text-align: right;
      margin-bottom: 12px;
      box-sizing: border-box;
    }

    .display::placeholder {
      color: #6b7280;
    }

    .mode-toggle {
      display: flex;
      justify-content: center;
      margin-bottom: 12px;
    }

    .mode-toggle button {
      flex: 1;
      margin: 0 4px;
      padding: 8px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      cursor: pointer;
      background: #3b82f6;
      color: white;
      transition: background 0.3s, transform 0.2s;
    }

    .mode-toggle button:hover {
      background: #2563eb;
      transform: translateY(-2px);
    }

    .buttons {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
    }

    button {
      padding: 14px;
      font-size: 16px;
      border: none;
      border-radius: 10px;
      background: #334155;
      color: #fff;
      cursor: pointer;
      transition: background 0.3s, transform 0.2s;
    }

    button:hover {
      background: #475569;
      transform: scale(1.05);
    }

    button:active {
      background: #2563eb;
      transform: scale(0.95);
    }

    .sci {
      display: none;
      margin-bottom: 8px;
    }

    /* History Panel */
    .history-panel {
      width: 250px;
      max-width: 80vw;
      background: #111827;
      border-radius: 15px;
      box-shadow: -4px 0 20px rgba(0,0,0,0.5);
      padding: 15px;
      transform: translateX(100%);
      transition: transform 0.5s ease-in-out;
      overflow-y: auto;
      max-height: 80vh;
    }

    .history-panel.active {
      transform: translateX(0);
    }

    .history-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .history-header h3 {
      margin: 0;
      font-size: 18px;
    }

    .clear-history {
      background: #ef4444;
      padding: 6px 10px;
      font-size: 12px;
    }

    .history-list {
      margin-top: 10px;
      font-size: 14px;
    }

    .toggle-history {
      position: absolute;
      top: 20px;
      right: 20px;
      background: #10b981;
      padding: 8px 12px;
      font-size: 14px;
    }

    @media (max-width: 768px) {
      .calculator-container {
        flex-direction: column;
        align-items: center;
      }
      .history-panel {
        position: fixed;
        right: 0;
        top: 0;
        bottom: 0;
      }
    }
  </style>
</head>
<body>
  <div class="calculator-container">
    <div class="calculator">
      <input type="text" id="display" class="display" placeholder="0" disabled>
      <div class="mode-toggle">
        <button onclick="setMode('basic')">Basic</button>
        <button onclick="setMode('sci')">Scientific</button>
      </div>

      <div class="buttons sci">
        <button onclick="append('math.sin(')">sin</button>
        <button onclick="append('math.cos(')">cos</button>
        <button onclick="append('math.tan(')">tan</button>
        <button onclick="append('math.sqrt(')">√</button>

        <button onclick="append('math.log(')">log</button>
        <button onclick="append('math.pi')">π</button>
        <button onclick="append('math.e')">e</button>
        <button onclick="append('**')">^</button>
      </div>

      <div class="buttons">
        <button onclick="append('7')">7</button>
        <button onclick="append('8')">8</button>
        <button onclick="append('9')">9</button>
        <button onclick="append('/')">÷</button>
        <button onclick="append('4')">4</button>
        <button onclick="append('5')">5</button>
        <button onclick="append('6')">6</button>
        <button onclick="append('*')">×</button>
        <button onclick="append('1')">1</button>
        <button onclick="append('2')">2</button>
        <button onclick="append('3')">3</button>
        <button onclick="append('-')">−</button>
        <button onclick="append('0')">0</button>
        <button onclick="append('.')">.</button>
        <button onclick="calculate()">=</button>
        <button onclick="append('+')">+</button>
      </div>
      <div style="margin-top: 12px; display: flex; gap: 8px;">
        <button onclick="clearDisplay()" style="background:#ef4444; flex-grow: 1;">Clear</button>
        <button onclick="backspace()" style="background:#f97316; flex-grow: 1;">DEL</button>
      </div>
    </div>

    <div class="history-panel" id="history-panel">
      <div class="history-header">
        <h3>History</h3>
        <button class="clear-history" onclick="clearHistory()">Delete</button>
      </div>
      <div class="history-list" id="history-list"></div>
    </div>
  </div>

  <button class="toggle-history" onclick="toggleHistory()">History</button>

  <script>
    let display = document.getElementById('display');
    let currentMode = 'basic';
    let historyList = document.getElementById('history-list');

    function append(value) {
      display.value += value;
    }

    function clearDisplay() {
      display.value = '';
    }

    function backspace() {
      display.value = display.value.slice(0, -1);
    }

    function calculate() {
      try {
        let result = eval(display.value);
        addHistory(display.value + ' = ' + result);
        display.value = result;
      } catch {
        display.value = 'Error';
      }
    }

    function setMode(mode) {
      currentMode = mode;
      document.querySelector('.sci').style.display = (mode === 'sci') ? 'grid' : 'none';
    }

    function toggleHistory() {
      document.getElementById('history-panel').classList.toggle('active');
    }

    function addHistory(entry) {
      let div = document.createElement('div');
      div.textContent = entry;
      historyList.prepend(div);
    }

    function clearHistory() {
      historyList.innerHTML = '';
    }

    // default mode
    setMode('basic');
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
