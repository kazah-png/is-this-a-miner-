## is this a miner? – Crypto Mining & Trading Simulator (GUI)

**is this a miner?** es un simulador de minería y trading de criptomonedas que imita el comportamiento de un minero/“virus”, pero es 100% inofensivo: **no mina criptomonedas reales, no se conecta a internet y no toca tus archivos ni tus datos personales**. Todo lo que ocurre es una simulación local.

El proyecto está escrito en **Python** y usa **Tkinter** para ofrecer una interfaz gráfica sencilla y accesible para cualquier persona, incluso si no está familiarizada con la consola.

## Características principales

- 🎮 **Simulación de minería**  
  - Minado por ticks (1, x10, x100) y modo **auto-minado** con actualización en tiempo real.  
  - Sistema de hash rate con mejoras de hardware (CPU, GPU, rigs, granjas mineras, etc.).

- 📊 **Mercado de criptomonedas simulado**  
  - Precios que fluctúan usando un modelo estocástico (estilo cripto real).  
  - Soporte para muchas monedas conocidas: BTC, ETH, BNB, DOGE, SOL, ADA, MATIC, DOT, SHIB, etc.  
  - Eventos de mercado: bull runs, crashes, FUD, pumps individuales.

- 💼 **Gestión de cartera (wallet)**  
  - Compra y venta de criptomonedas con dinero fiat.  
  - Impuestos simulados, costes eléctricos y valor total del portfolio en tiempo real.  

- 🧩 **Mejoras temporales (run actual)**  
  - Hardware (hash rate) y utilidades (menos electricidad, menos impuestos, seguros contra hack y fallos de hardware).  
  - Desbloqueo de nuevos packs de criptomonedas.

- 🔁 **Sistema de Prestigio**  
  - Reinicia tu partida a cambio de **puntos de prestigio**.  
  - Árbol de **mejoras permanentes**: más hash global, menos impuestos, mejor electricidad, eventos de mercado más favorables y desbloqueos extra al inicio.  
  - **Bots de trading** comprados con prestigio (DCA BTC, scalper de volatilidad, rebalanceo a stablecoins).

- ⛓ **DeFi / Staking**  
  - Staking para criptos como ETH, ADA, SOL, MATIC, DOT con intereses por tick.  

- 📝 **Misiones diarias/semanales/mensuales**  
  - Objetivos de minado, valor de cartera y desbloqueos.  
  - Recompensas en puntos de prestigio adicionales.

- 🖥️ **Interfaz gráfica amigable (Tkinter)**  
  - Pestañas: *Dashboard, Mercado, Mejoras, Misiones, Prestigio, Staking, Ayuda*.  
  - Tablero con wallet, resumen de misiones, eventos recientes y estado del mercado.  
  - Controles con botones, listas y cuadros de texto: pensado para usuarios que no usan CMD.

## Tecnologías

- Python 3.x  
- Tkinter (GUI estándar de Python)  
- PyInstaller (opcional, para generar ejecutables `.exe` en Windows)

## Ejecución

```bash
python is_this_a_miner_gui.py
