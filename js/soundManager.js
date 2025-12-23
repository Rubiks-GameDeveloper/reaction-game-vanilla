class SoundManager {
    constructor() {
        this.sounds = {};
        this.isMuted = false;
        this.backgroundMusicId = null;
        this.loadSounds();
    }

    loadSounds() {
        const soundFiles = {
            hit: 'sounds/ClickEffect.wav',
            gameOver: 'sounds/game-over.mp3',
            achievement: 'sounds/ClickEffect.wav', // Используем тот же звук, так как achievement.mp3 может отсутствовать
            background: 'sounds/BackgroundMusic.mp3'
        };

        for (const [name, path] of Object.entries(soundFiles)) {
            this.sounds[name] = new Audio(path);
            this.sounds[name].volume = 0.5;
        }
    }

    play(soundName) {
        if (this.isMuted || !this.sounds[soundName]) return;
        
        const sound = this.sounds[soundName];
        sound.currentTime = 0;
        sound.play().catch(error => console.log('Error playing sound:', error));
    }

    startBackgroundMusic() {
        if (this.isMuted || this.backgroundMusicId) return;
        
        const music = this.sounds.background;
        music.loop = true;
        music.volume = 0.3;
        music.play().catch(error => console.log('Error playing background music:', error));
        this.backgroundMusicId = music;
    }

    pauseBackgroundMusic() {
        if (this.backgroundMusicId) {
            this.backgroundMusicId.pause();
        }
    }

    resumeBackgroundMusic() {
        if (this.backgroundMusicId && !this.isMuted) {
            this.backgroundMusicId.play().catch(error => console.log('Error resuming background music:', error));
        }
    }
}

const soundManager = new SoundManager(); 