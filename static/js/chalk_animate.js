/**
 * Chalk Writing Animation Helper
 * Animates text word-by-word to simulate classroom writing.
 */
window.animateChalkText = function(containerId, text, wordsPerSecond = 6) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`[Genius Chalk] Container with ID '${containerId}' not found.`);
        return;
    }
    
    // Split text by space but preserve line breaks
    const tokens = text.split(/(\s+)/);
    container.innerHTML = '';
    
    let wordIndex = 0;
    tokens.forEach((token) => {
        if (!token) return;
        
        if (token.match(/\s+/)) {
            // It's a space or newline
            if (token.includes('\n')) {
                const brs = token.split('\n').length - 1;
                for (let b = 0; b < brs; b++) {
                    container.appendChild(document.createElement('br'));
                }
            } else {
                container.appendChild(document.createTextNode(' '));
            }
        } else {
            // It's a word
            const span = document.createElement('span');
            span.className = 'chalk-word';
            span.textContent = token;
            span.style.animationDelay = `${wordIndex / wordsPerSecond}s`;
            container.appendChild(span);
            wordIndex++;
        }
    });
};
