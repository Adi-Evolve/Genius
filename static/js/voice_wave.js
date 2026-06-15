/**
 * Voice Wave Visualizer Helper
 * Dynamically scales the height of waveform bars to simulate active listening/speaking.
 */
window.initVoiceWave = function(containerId, barCount = 5) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    container.style.display = 'none';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'center';
    container.style.height = '40px';
    container.style.gap = '3px';
    
    const bars = [];
    for (let i = 0; i < barCount; i++) {
        const bar = document.createElement('div');
        bar.className = 'wave-bar';
        container.appendChild(bar);
        bars.push(bar);
    }
    
    let intervalId = null;
    
    window.startVoiceWaveAnimation = function() {
        container.style.display = 'flex';
        if (intervalId) clearInterval(intervalId);
        
        intervalId = setInterval(() => {
            bars.forEach(bar => {
                // Random height scaling for natural audio wave appearance
                const height = 4 + Math.random() * 24;
                bar.style.height = `${height}px`;
            });
        }, 80);
    };
    
    window.stopVoiceWaveAnimation = function() {
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
        container.style.display = 'none';
        bars.forEach(bar => {
            bar.style.height = '4px';
        });
    };
};
