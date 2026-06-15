/**
 * Classroom Microphone Audio Bridge
 * Captures microphone stream when the teacher presses/holds the mic button,
 * and writes the captured audio as a base64 string into a hidden Streamlit text input.
 * Uses event delegation on document so listeners survive Streamlit reruns.
 */
(function() {
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let stream = null;
    let currentMicBtn = null;

    // Helper to find the hidden Streamlit input element and inject the base64 audio
    function writeToStreamlit(base64Audio) {
        const hiddenContainer = document.getElementById('hidden_audio_input_container');
        let inputEl = null;
        if (hiddenContainer) {
            inputEl = hiddenContainer.querySelector('input');
        } else {
            inputEl = document.querySelector('input[aria-label="Hidden Audio Base64"]');
        }

        if (inputEl) {
            console.log("[AudioBridge] Injecting audio data into Streamlit input.");
            inputEl.value = base64Audio;
            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
            inputEl.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
            console.warn("[AudioBridge] Hidden Streamlit audio input element not found in DOM.");
        }
    }

    function setRecordingState(active) {
        isRecording = active;
        const btn = document.querySelector('.mic-circle-btn') || currentMicBtn;
        if (btn) {
            if (active) {
                btn.classList.add('recording');
                if (window.startVoiceWaveAnimation) {
                    window.startVoiceWaveAnimation();
                }
            } else {
                btn.classList.remove('recording');
                if (window.stopVoiceWaveAnimation) {
                    window.stopVoiceWaveAnimation();
                }
            }
        }
    }

    async function startRecording(btn) {
        currentMicBtn = btn;
        audioChunks = [];
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const options = { mimeType: 'audio/webm' };
            mediaRecorder = new MediaRecorder(stream, options);
            
            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64Data = reader.result.split(',')[1];
                    writeToStreamlit(base64Data);
                };
                reader.readAsDataURL(audioBlob);
                
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            };
            
            mediaRecorder.start(100);
            setRecordingState(true);
        } catch (err) {
            console.error("[AudioBridge] Microphone access failed: ", err);
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        setRecordingState(false);
    }

    // Initialize global event delegation on document load
    document.addEventListener('mousedown', async (e) => {
        const btn = e.target.closest('.mic-circle-btn');
        if (btn) {
            e.preventDefault();
            await startRecording(btn);
        }
    });

    document.addEventListener('mouseup', (e) => {
        if (isRecording) {
            e.preventDefault();
            stopRecording();
        }
    });

    document.addEventListener('mouseout', (e) => {
        if (isRecording && e.target.closest('.mic-circle-btn')) {
            // Check if we actually left the button boundary
            const destination = e.relatedTarget;
            if (!destination || !destination.closest('.mic-circle-btn')) {
                stopRecording();
            }
        }
    });

    // Touch events for smart board/mobile screens
    document.addEventListener('touchstart', async (e) => {
        const btn = e.target.closest('.mic-circle-btn');
        if (btn) {
            e.preventDefault();
            await startRecording(btn);
        }
    }, { passive: false });

    document.addEventListener('touchend', (e) => {
        if (isRecording) {
            e.preventDefault();
            stopRecording();
        }
    }, { passive: false });

    console.log("[AudioBridge] Global event delegation listeners initialized.");
})();

