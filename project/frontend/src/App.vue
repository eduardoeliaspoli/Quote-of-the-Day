<template>
  <div :class="['app', { 'dark-mode': isDarkMode }]">

    <div class="lottie-background">
       <Vue3Lottie
          v-if="rocketAnimation"
          :animationData="rocketAnimation"
          :autoplay="true"
          :loop="true"
          :speed="0.7"
          class="lottie-bg lottie-rocket"
       />
       <Vue3Lottie
          v-if="planetDiscAnimation"
          :animationData="planetDiscAnimation"
          :autoplay="true"
          :loop="true"
          :speed="0.3"
          class="lottie-bg lottie-planet-disc"
        />
       <Vue3Lottie
          v-if="searchingAnimation"
          :animationData="searchingAnimation"
          :autoplay="true"
          :loop="true"
          :speed="0.5"
          class="lottie-bg lottie-searching"
        />
        <Vue3Lottie
          v-if="astronautAnimation"
          :animationData="astronautAnimation"
          :autoplay="true"
          :loop="true"
          :speed="0.4"
          class="lottie-bg lottie-astronaut"
        />
       <Vue3Lottie
         v-if="orbitAnimation"
         :animationData="orbitAnimation"
         :autoplay="true"
         :loop="true"
         :speed="0.2"
         class="lottie-bg lottie-orbit"
        />
       <Vue3Lottie
         v-if="galaxyAnimation"
         :animationData="galaxyAnimation"
         :autoplay="true"
         :loop="true"
         :speed="0.1"
         class="lottie-bg lottie-galaxy"
        />
       <Vue3Lottie
         v-if="alienRocketAnimation"
         :animationData="alienRocketAnimation"
         :autoplay="true"
         :loop="true"
         :speed="1"
         class="lottie-bg lottie-alien-rocket"
        />
       </div>

    <div class="content-wrapper">
      <div class="info-bar">
        <div class="info-content">
          <div class="datetime">
            <div class="date">{{ currentDate }}</div>
            <div class="time" v-if="lastUpdated">Atualizado às {{ lastUpdated }}</div>
          </div>

          <button
            @click="toggleTheme"
            class="theme-toggle"
            :aria-label="isDarkMode ? 'Ativar tema claro' : 'Ativar tema escuro'"
          >
            <span v-if="isDarkMode"><Sun class="w-6 h-6"/></span>
            <span v-else><Moon class="w-6 h-6"/></span>
          </button>
        </div>
      </div>

      <main class="main-content">
        <transition name="fade" mode="out-in">
          <div v-if="loading" key="loading" class="center-content">
             <Vue3Lottie
                v-if="searchingAnimation"
               :animationData="searchingAnimation"
               :autoplay="true"
               :loop="true"
               :speed="1"
               class="loading-lottie"
             />
             <p class="loading-text">Carregando...</p>
          </div>

          <div v-else-if="quote && quote.frase && !error" key="quote" class="quote-section">
            <h1 class="main-title">Frase do Dia</h1>
            <blockquote class="quote">
              <p class="quote-text">{{ quote.frase }}</p>
              <footer class="quote-footer">
                <cite>— {{ quote.autor || 'Desconhecido' }}</cite>
              </footer>
            </blockquote>

            <div class="button-container">
              <button
                @click="fetchNewQuote"
                :disabled="loading"
                class="refresh-btn"
              >
                <span class="refresh-icon" :class="{ rotating: loading && activeFetch === 'json' }">
                    <RotateCcw class="w-5 h-5"/>
                 </span>
                Nova Frase
              </button>
              <button
                @click="fetchAiQuote"
                :disabled="loading"
                class="refresh-btn ai-btn"
              >
                 <span class="refresh-icon" :class="{ rotating: loading && activeFetch === 'ia' }">
                    <Sparkles class="w-5 h-5"/>
                 </span>
                Gerar com IA
              </button>
            </div>
          </div>

          <div v-else-if="error" key="error" class="center-content error-container">
              <Vue3Lottie
                  v-if="astronautAnimation"
                  :animationData="astronautAnimation"
                  :autoplay="true"
                  :loop="true"
                  :speed="0.5"
                  class="error-lottie"
              />
             <p class="error-text">{{ error }}</p>
             <button @click="fetchNewQuote" class="retry-btn">
               Tentar Novamente (JSON)
             </button>
           </div>
        </transition>
      </main>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { Sun, Moon, RotateCcw, Sparkles } from "lucide-vue-next";
// Substituído o import do player Lottie
import { Vue3Lottie } from 'vue3-lottie';


import rocketAnimation from '../assets/Rocket in Space (Transparent Background).json';
import planetDiscAnimation from '../assets/Planet with disc.json';
import searchingAnimation from '../assets/AI Searching.json';
import astronautAnimation from '../assets/Cute astronaut read book on planet cartoon.json';
import orbitAnimation from '../assets/Planet Orbit.json';
import galaxyAnimation from '../assets/Milky way Galaxy.json';
import alienRocketAnimation from '../assets/Alien going to space emoji animation.json';


const quote = ref(null);
const loading = ref(false);
const error = ref(null);
const lastUpdated = ref('');
const isDarkMode = ref(false);
const activeFetch = ref('');

const API_BASE = 'https://quote-of-the-day-raps.onrender.com/'; // Ou seu endereço de API
let dayCheckerInterval = null;

const currentDate = computed(() => {
  return new Date().toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
});

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value;
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
}

async function fetchNewQuote() {
  loading.value = true;
  activeFetch.value = 'json';
  error.value = null;

  try {
    const response = await fetch(`${API_BASE}/api/frase`);
    if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    quote.value = data;
    lastUpdated.value = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  } catch (err) {
    console.error("Erro ao buscar frase do JSON:", err);
    error.value = 'Não foi possível carregar a frase (JSON).';
  } finally {
    loading.value = false;
    activeFetch.value = '';
  }
}

async function fetchAiQuote() {
  loading.value = true;
  activeFetch.value = 'ia';
  error.value = null;

  try {
    const response = await fetch(`${API_BASE}/api/frase/ia`);
    if (!response.ok) {
      const errData = await response.json().catch(() => ({ error: `Erro HTTP: ${response.status}` }));
      throw new Error(errData.error || `Erro HTTP: ${response.status}`);
    }
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    quote.value = data;
    lastUpdated.value = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  } catch (err) {
    console.error("Erro ao gerar frase com IA:", err);
    error.value = `Não foi possível gerar com IA: ${err.message}`;
  } finally {
    loading.value = false;
    activeFetch.value = '';
  }
}

function checkNewDay() {
  const today = new Date().toDateString();
  const lastDay = localStorage.getItem('ultimoDiaFrase');

  if (lastDay !== today) {
    localStorage.setItem('ultimoDiaFrase', today);
    fetchNewQuote(); // Mantém o JSON como fonte da "Frase do Dia"
    return true;
  }
  return false;
}

function startDayChecker() {
  dayCheckerInterval = setInterval(checkNewDay, 60000); // Verifica a cada minuto
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  isDarkMode.value = savedTheme === 'dark'; // Default para light se não houver preferência salva

  if (!checkNewDay()) {
    fetchNewQuote();
  }
  startDayChecker();
});

onUnmounted(() => {
  if (dayCheckerInterval) {
    clearInterval(dayCheckerInterval);
  }
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden; /* Evita scroll horizontal */
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>

<style scoped>
/* Variáveis de Tema */
:root, .app {
  --bg-color: #ffffff;
  --text-color: #000000;
  --bg-gradient: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
  --info-bg: rgba(255, 255, 255, 0.5);
  --info-border: rgba(0, 0, 0, 0.1);
  --button-bg: rgba(0, 0, 0, 0.1);
  --button-border: rgba(0, 0, 0, 0.2);
  --button-hover-bg: rgba(0, 0, 0, 0.2);
  --quote-text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.1);
  --title-text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
  --icon-color: #333;
  --link-color: #007bff;
  --link-hover-color: #0056b3;
}

.app.dark-mode {
  --bg-color: #000000;
  --text-color: #ffffff;
  --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  --info-bg: rgba(0, 0, 0, 0.5);
  --info-border: rgba(255, 255, 255, 0.1);
  --button-bg: rgba(255, 255, 255, 0.1);
  --button-border: rgba(255, 255, 255, 0.2);
  --button-hover-bg: rgba(255, 255, 255, 0.2);
  --quote-text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.4);
  --title-text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.4);
  --icon-color: #eee;
  --link-color: #64b5f6;
  --link-hover-color: #90caf9;
}

.app {
  min-height: 100vh;
  width: 100%;
  background: var(--bg-gradient);
  color: var(--text-color);
  display: flex;
  flex-direction: column;
  transition: background 0.5s ease, color 0.5s ease;
  position: relative;
  overflow: hidden;
}

/* Container para animações de fundo */
.lottie-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

/* Estilos base para os Lotties de fundo */
.lottie-bg {
  position: absolute;
  opacity: 0.15;
  pointer-events: none;
  filter: var(--lottie-filter, none);
  transition: opacity 0.5s ease;
}

.dark-mode .lottie-bg {
  opacity: 0.2;
}

/* Posicionamento e tamanho específicos para cada Lottie */
.lottie-rocket { top: 20%; left: 5%; width: 120px; height: 120px; transform: rotate(-30deg); opacity: 0.1;}
.lottie-planet-disc { top: 15%; right: 10%; width: 180px; height: 180px; opacity: 0.2;}
.lottie-searching { bottom: 5%; left: 15%; width: 100px; height: 100px; opacity: 0.15;}
.lottie-astronaut { bottom: 10%; right: 8%; width: 150px; height: 150px; transform: rotate(15deg); opacity: 0.1;}
.lottie-orbit { top: 60%; left: 5%; width: 200px; height: 200px; opacity: 0.1;}
.lottie-galaxy { top: 6%; right: 40%; width: 250px; height: 250px; opacity: 0.08;}
.lottie-alien-rocket { bottom: 25%; left: 3%; width: 80px; height: 80px; transform: rotate(45deg) scaleX(-1); opacity: 0.1;}
/* Adicione mais classes e estilos para as outras animações aqui */

/* Wrapper do conteúdo principal */
.content-wrapper {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Info Bar */
.info-bar {
  background: var(--info-bg);
  border-bottom: 1px solid var(--info-border);
  backdrop-filter: blur(10px);
  padding: 1rem 1.5rem;
  transition: background-color 0.5s ease, border-color 0.5s ease;
}

.info-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.datetime { display: flex; flex-direction: column; gap: 0.25rem; }
.date { font-size: 0.95rem; font-weight: 600; text-transform: capitalize; }
.time { font-size: 0.8rem; opacity: 0.8; }

/* Botão de tema */
.theme-toggle {
  background: var(--button-bg);
  border: 1px solid var(--button-border);
  color: var(--icon-color);
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.25rem;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}
.theme-toggle svg { transition: color 0.5s ease; }
.theme-toggle:hover {
  background: var(--button-hover-bg);
  transform: scale(1.05);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
}

.center-content { text-align: center; max-width: 600px; }

/* Quote Section */
.quote-section {
  width: 100%;
  max-width: 900px;
  text-align: center;
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.main-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  letter-spacing: -0.02em;
  text-shadow: var(--title-text-shadow);
}

.quote { margin-bottom: 3rem; }

.quote-text {
  font-size: 2rem;
  line-height: 1.5;
  font-weight: 300;
  margin-bottom: 2rem;
  text-shadow: var(--quote-text-shadow);
}

.quote-footer { font-size: 1.25rem; opacity: 0.9; }
.quote-footer cite { font-style: normal; font-weight: 500; }

/* Button Container */
.button-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
}

/* Buttons */
.refresh-btn,
.retry-btn {
  background: var(--button-bg);
  border: 1px solid var(--button-border);
  color: var(--text-color);
  padding: 0.9rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
}

.refresh-btn svg, .retry-btn svg {
  color: var(--icon-color);
  transition: color 0.5s ease;
}

.refresh-btn:hover:not(:disabled),
.retry-btn:hover {
  background: var(--button-hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.refresh-btn:active:not(:disabled),
.retry-btn:active {
  transform: translateY(0);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  display: inline-block;
  line-height: 1;
}

.refresh-icon.rotating {
  animation: spin 1s linear infinite;
}

/* Loading */
.loading-lottie {
  width: 100px;
  height: 100px;
  margin: 0 auto 1rem;
}

/* Error */
.error-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.error-lottie {
  width: 150px;
  height: 150px;
  margin-bottom: 1rem;
}
.error-text {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  opacity: 0.9;
  max-width: 400px;
}


/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.fade-enter-from { opacity: 0; transform: translateY(20px); }
.fade-leave-to { opacity: 0; transform: translateY(-20px); }

/* Spin Animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .info-bar { padding: 0.875rem 1rem; }
  .date { font-size: 0.85rem; }
  .time { font-size: 0.75rem; }
  .main-title { font-size: 2rem; }
  .quote-text { font-size: 1.5rem; }
  .quote-footer { font-size: 1.05rem; }
  .refresh-btn, .retry-btn { padding: 0.875rem 1.5rem; font-size: 0.9rem; }
  .button-container { gap: 1rem; }

  .lottie-rocket { width: 80px; height: 80px; top: 20%; left: 3%;}
  .lottie-planet-disc { width: 120px; height: 120px; top: 12%; right: 5%;}
  .lottie-searching { width: 70px; height: 70px; bottom: 3%; left: 10%;}
  .lottie-astronaut { width: 100px; height: 100px; bottom: 5%; right: 4%;}
  .lottie-orbit { width: 150px; height: 150px; top: 55%; left: 2%; opacity: 0.08;}
  .lottie-galaxy { width: 180px; height: 180px; top: 3%; right: 30%; opacity: 0.05;}
  .lottie-alien-rocket { width: 60px; height: 60px; bottom: 20%; left: 1%;}
}

@media (max-width: 480px) {
  .main-title { font-size: 1.75rem; margin-bottom: 2rem; }
  .quote-text { font-size: 1.25rem; }
  .quote-footer { font-size: 0.95rem; }
  .quote { margin-bottom: 2rem; }
  .button-container { flex-direction: column; align-items: center; gap: 1rem; }
  .refresh-btn, .retry-btn { width: 80%; max-width: 300px; justify-content: center; }

  .lottie-orbit, .lottie-galaxy, .lottie-alien-rocket { display: none; }
  .lottie-rocket { width: 60px; height: 60px; top: 20%; }
  .lottie-planet-disc { width: 90px; height: 90px; top: 8%; }
  .lottie-astronaut { width: 80px; height: 80px; bottom: 3%; }
}

/* Acessibilidade */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  .rotating { animation: none !important; }
}
</style>