"""🎤 Componente de Microfone para o DocScripta AI

Usa a Web Speech API nativa do navegador.
ZERO dependências Python extras — funciona direto!

Compatível com: Chrome, Edge, Safari, Chrome Android
NÃO funciona: Firefox

COMO FUNCIONA:
1. Usuário clica no 🎤
2. Navegador grava a voz e transcreve em tempo real
3. Texto transcrito aparece na tela
4. Usuário copia e cola no campo de texto, OU
5. O texto é injetado automaticamente via JavaScript

Uso no app.py:
    from voz_microfone import componente_microfone
    
    # Na página de Síntese Acadêmica, ANTES do text_area:
    componente_microfone()
    
    # O text_area normal:
    texto = st.text_area(
        "Cole seu texto ou use o 🎤:",
        height=300,
        key="texto_entrada"
    )
"""

import streamlit as st
import streamlit.components.v1 as components


def componente_microfone():
    """
    Exibe um botão de microfone 🎤 na página.
    
    O texto transcrito aparece abaixo do botão
    e o usuário pode clicar para adicioná-lo
    ao campo de texto.
    """

    # ---- Componente HTML com tudo embutido ----
    # O JS injeta o texto diretamente no textarea
    # do Streamlit usando manipulação do DOM
    html_code = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    overflow: hidden;
    background: transparent;
  }
  .mic-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0;
  }
  .mic-btn {
    background: linear-gradient(135deg, #1E88E5, #1565C0);
    color: white;
    border: none;
    border-radius: 50%;
    width: 52px;
    height: 52px;
    font-size: 26px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 3px 12px rgba(30,136,229,0.4);
    flex-shrink: 0;
  }
  .mic-btn:hover { transform: scale(1.08); }
  .mic-btn:active { transform: scale(0.95); }
  .mic-btn.recording {
    background: linear-gradient(135deg, #ff4444, #cc0000) !important;
    animation: pulse 1.5s infinite;
  }
  .mic-btn.disabled {
    opacity: 0.4;
    cursor: not-allowed;
    background: #999 !important;
  }
  .mic-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }
  .mic-status {
    font-size: 14px;
    color: #888;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .mic-status.success { color: #4CAF50; font-weight: bold; }
  .mic-status.error { color: #ff4444; }
  .mic-status.listening { color: #1E88E5; font-weight: bold; }
  .mic-hint {
    font-size: 11px;
    color: #aaa;
  }
  .mic-result {
    display: none;
    margin-top: 8px;
    padding: 10px 14px;
    background: #f0f8f0;
    border: 1px solid #4CAF50;
    border-radius: 8px;
    font-size: 14px;
    color: #333;
    word-wrap: break-word;
  }
  .mic-result.visible { display: block; }
  .mic-add-btn {
    margin-top: 6px;
    padding: 6px 16px;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .mic-add-btn:hover { background: #388E3C; }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255,68,68,0.7); }
    70% { box-shadow: 0 0 0 14px rgba(255,68,68,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,68,68,0); }
  }
</style>
</head>
<body>

<div class="mic-wrapper">
  <button class="mic-btn" id="micBtn" type="button">🎤</button>
  <div class="mic-info">
    <span class="mic-status" id="micStatus">Clique para falar</span>
    <span class="mic-hint" id="micHint">Gravação de voz em português</span>
  </div>
</div>
<div class="mic-result" id="micResult"></div>

<script>
(function() {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var btn = document.getElementById('micBtn');
  var status = document.getElementById('micStatus');
  var hint = document.getElementById('micHint');
  var result = document.getElementById('micResult');
  var textoAcumulado = '';

  if (!SpeechRecognition) {
    status.textContent = '⚠️ Use Chrome ou Edge para microfone';
    status.className = 'mic-status error';
    btn.className = 'mic-btn disabled';
    btn.onclick = function() {};
    return;
  }

  var recognition = new SpeechRecognition();
  recognition.lang = 'pt-BR';
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.maxAlternatives = 1;

  var isRecording = false;

  btn.onclick = function() {
    if (isRecording) {
      recognition.stop();
      return;
    }
    isRecording = true;
    btn.innerHTML = '⏹️';
    btn.classList.add('recording');
    status.textContent = '🎤 Ouvindo...';
    status.className = 'mic-status listening';
    hint.textContent = 'Fale agora. Clique ⏹️ para parar.';
    recognition.start();
  };

  recognition.onresult = function(event) {
    var finalText = '';
    var interimText = '';

    for (var i = event.resultIndex; i < event.results.length; i++) {
      var t = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalText += t + ' ';
      } else {
        interimText += t;
      }
    }

    if (interimText) {
      status.textContent = '🎤 ' + interimText;
    }

    if (finalText.trim()) {
      textoAcumulado += finalText.trim() + ' ';
      status.textContent = '✅ Texto capturado!';
      status.className = 'mic-status success';
      hint.textContent = 'Clique novamente para falar mais';
      result.textContent = textoAcumulado.trim();
      result.classList.add('visible');

      // TENTAR injetar no textarea do Streamlit
      // O Streamlit renderiza textareas com atributos data
      // Vamos procurar o textarea visível mais próximo
      try {
        var parentDoc = window.parent.document;
        if (parentDoc) {
          // Procurar o textarea dentro do container pai
          var textareas = parentDoc.querySelectorAll('textarea[aria-label]');
          var target = null;
          // Pegar o primeiro textarea visível
          for (var j = 0; j < textareas.length; j++) {
            if (textareas[j].offsetParent !== null) {
              target = textareas[j];
              break;
            }
          }
          if (target) {
            var existing = target.value || '';
            target.value = existing + (existing ? '\n' : '') + finalText.trim();
            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
            result.innerHTML = '✅ Texto adicionado ao campo abaixo!<br><small>"' + finalText.trim() + '"</small>';
          }
        }
      } catch(e) {
        // Cross-origin — não consegue acessar o DOM pai
        // Mostrar o texto para o usuário copiar
        result.innerHTML = '📋 Copie e cole no campo abaixo:<br><strong>"' + finalText.trim() + '"</strong>';
      }
    }
  };

  recognition.onend = function() {
    isRecording = false;
    btn.innerHTML = '🎤';
    btn.classList.remove('recording');
    if (status.textContent.indexOf('Ouvindo') >= 0) {
      status.textContent = 'Clique para falar';
      status.className = 'mic-status';
      hint.textContent = 'Gravação de voz em português';
    }
  };

  recognition.onerror = function(event) {
    isRecording = false;
    btn.innerHTML = '🎤';
    btn.classList.remove('recording');
    if (event.error === 'no-speech') {
      status.textContent = '🔇 Nenhum áudio. Tente novamente.';
    } else if (event.error === 'not-allowed') {
      status.textContent = '🚫 Permita o microfone.';
    } else {
      status.textContent = '❌ Erro: ' + event.error;
    }
    status.className = 'mic-status error';
    hint.textContent = '';
  };
})();
</script>
</body>
</html>
"""

    # Renderizar componente
    components.html(
        html_code,
        height=100,
    )
