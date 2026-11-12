	import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.2';

	const statusEl = document.getElementById('status');
	const outputEl = document.getElementById('output');
	const translateBtn = document.getElementById('translateBtn');
	const toggleDirBtn = document.getElementById('toggleDirBtn');
	const inputTextEl = document.getElementById('inputText');

	let currentDirection = 'en-es'; 
	let translators = {};

	async function initTranslators() {
		try {
			const supportsWebGPU = typeof navigator !== "undefined" && "gpu" in navigator;
			const device = supportsWebGPU ? 'webgpu' : 'wasm';
			
			statusEl.innerText = `Cargando modelos optimizados (Aceleración: ${device.toUpperCase()})...`;
			

			translators['en-es'] = await pipeline('translation', 'Xenova/opus-mt-en-es', { device });
			translators['es-en'] = await pipeline('translation', 'Xenova/opus-mt-es-en', { device });

			statusEl.innerText = "Modelos listos para usar offline.";
			translateBtn.disabled = false;
		} catch (error) {
			statusEl.innerText = "Error al cargar los modelos: " + error.message;
			console.error(error);
		}
	}

	toggleDirBtn.addEventListener('click', () => {
		if (currentDirection === 'en-es') {
			currentDirection = 'es-en';
			toggleDirBtn.innerText = "Dirección: Español ➔ Inglés";
			inputTextEl.placeholder = "Escribe algo en español...";
		} else {
			currentDirection = 'en-es';
			toggleDirBtn.innerText = "Dirección: Inglés ➔ Español";
			inputTextEl.placeholder = "Write something in English...";
		}
	});

	async function translateText() {
		const text = inputTextEl.value.trim();
		if (!text) return;

		statusEl.innerText = "Traduciendo...";
		translateBtn.disabled = true;

		try {
			const translator = translators[currentDirection];
			const result = await translator(text);
			outputEl.innerText = result[0].translation_text;
			statusEl.innerText = "¡Traducción completada!";
		} catch (error) {
			statusEl.innerText = "Error durante el proceso de traducción.";
			outputEl.innerText = error.message;
			console.error(error);
		} finally {
			translateBtn.disabled = false;
		}
	}

	translateBtn.addEventListener('click', translateText);
	initTranslators();
