with open("fuzzy-front-end.html", "r") as f:
    text = f.read()

new_text = text.replace("""                ws.onmessage = async (event) => {
                    if (event.data instanceof ArrayBuffer) {
                        const int16Array = new Int16Array(event.data);
                        const float32Array = new Float32Array(int16Array.length);
                        for (let i = 0; i < int16Array.length; i++) {
                            float32Array[i] = int16Array[i] / (int16Array[i] < 0 ? 0x8000 : 0x7FFF);
                        }
                        const audioBuffer = audioContext.createBuffer(1, float32Array.length, 24000);
                        audioBuffer.getChannelData(0).set(float32Array);
                        const source = audioContext.createBufferSource();
                        source.buffer = audioBuffer;
                        source.connect(audioContext.destination);
                        source.start();
                        setVoiceState('responding');
                    }
                };""", """                let nextPlayTime = 0;

                ws.onmessage = async (event) => {
                    if (event.data instanceof ArrayBuffer) {
                        const int16Array = new Int16Array(event.data);
                        const float32Array = new Float32Array(int16Array.length);
                        for (let i = 0; i < int16Array.length; i++) {
                            float32Array[i] = int16Array[i] / (int16Array[i] < 0 ? 0x8000 : 0x7FFF);
                        }
                        const audioBuffer = audioContext.createBuffer(1, float32Array.length, 24000);
                        audioBuffer.getChannelData(0).set(float32Array);
                        const source = audioContext.createBufferSource();
                        source.buffer = audioBuffer;
                        source.connect(audioContext.destination);

                        if (nextPlayTime < audioContext.currentTime) {
                            nextPlayTime = audioContext.currentTime;
                        }
                        source.start(nextPlayTime);
                        nextPlayTime += audioBuffer.duration;

                        setVoiceState('responding');
                    }
                };""")

with open("fuzzy-front-end.html", "w") as f:
    f.write(new_text)

print("Patched overlapping audio!")
