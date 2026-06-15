/**
 * Keyboard Shortcuts Handler for Genius
 * Allows teachers to operate the co-pilot hands-free/keyboard-only.
 * Hotkeys:
 * - Ctrl + M : Toggle Microphone recording
 * - Ctrl + Q : Switch immediately to Quiz Mode
 * - Ctrl + C : Wipe chalkboard clean
 * - Escape   : Stop voice playback / exit modal
 */
(function() {
    document.addEventListener('keydown', function(event) {
        // 1. Ctrl + M (Microphone)
        if (event.ctrlKey && event.key.toLowerCase() === 'm') {
            event.preventDefault();
            console.log("[Genius Keybind] Ctrl+M detected. Triggering mic...");
            // Look for both main board mic button and landing screen mic
            const micBtn = document.querySelector('button[key*="mic"]') || 
                           document.querySelector('button[key*="board_mic"]');
            if (micBtn) {
                micBtn.click();
            } else {
                // Click the primary microphone emoji button inside col_mic
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.innerText.includes('🎤') || btn.innerText.includes('🛑')) {
                        btn.click();
                        break;
                    }
                }
            }
        }
        
        // 2. Ctrl + Q (Quiz Mode)
        if (event.ctrlKey && event.key.toLowerCase() === 'q') {
            event.preventDefault();
            console.log("[Genius Keybind] Ctrl+Q detected. Switching to Quiz...");
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                const text = btn.innerText || btn.textContent || "";
                if (text.includes('Voice Quiz')) {
                    btn.click();
                    break;
                }
            }
        }
        
        // 3. Ctrl + C (Clear Board)
        if (event.ctrlKey && event.key.toLowerCase() === 'c') {
            event.preventDefault();
            console.log("[Genius Keybind] Ctrl+C detected. Erasing board...");
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                const text = btn.innerText || btn.textContent || "";
                if (text.includes('Wipe Chalkboard')) {
                    btn.click();
                    break;
                }
            }
        }
        
        // 4. Escape (Stop voice / reset)
        if (event.key === 'Escape') {
            event.preventDefault();
            console.log("[Genius Keybind] Escape detected. Stopping voice playback...");
            const audioEl = document.querySelector('audio');
            if (audioEl) {
                audioEl.pause();
                audioEl.remove();
            }
        }
    });
})();
