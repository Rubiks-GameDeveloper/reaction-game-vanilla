export function useSoundManager() {
  const sounds = {}
  let isMuted = false
  let backgroundMusic = null

  const loadSounds = () => {
    const soundFiles = {
      hit: '/sounds/ClickEffect.wav',
      gameOver: '/sounds/game-over.mp3',
      achievement: '/sounds/ClickEffect.wav',
      background: '/sounds/BackgroundMusic.mp3'
    }

    for (const [name, path] of Object.entries(soundFiles)) {
      sounds[name] = new Audio(path)
      sounds[name].volume = 0.5
    }
  }

  const play = (soundName) => {
    if (isMuted || !sounds[soundName]) return
    
    const sound = sounds[soundName]
    sound.currentTime = 0
    sound.play().catch(error => console.log('Error playing sound:', error))
  }

  const startBackgroundMusic = () => {
    if (!sounds.background) return
    
    const music = sounds.background
    backgroundMusic = music
    
    if (isMuted) return
    
    if (!music.paused) return // Already playing
    
    music.loop = true
    music.volume = 0.3
    music.play().catch(error => console.log('Error playing background music:', error))
  }

  const pauseBackgroundMusic = () => {
    if (backgroundMusic) {
      backgroundMusic.pause()
    } else if (sounds.background) {
      sounds.background.pause()
    }
  }

  const resumeBackgroundMusic = () => {
    if (!backgroundMusic && sounds.background) {
      backgroundMusic = sounds.background
    }
    
    if (backgroundMusic && !isMuted) {
      backgroundMusic.loop = true
      backgroundMusic.volume = 0.3
      backgroundMusic.play().catch(error => console.log('Error resuming background music:', error))
    }
  }

  const setMuted = (muted) => {
    isMuted = muted
    if (muted) {
      pauseBackgroundMusic()
    } else if (backgroundMusic) {
      // Only resume if music was already started
      resumeBackgroundMusic()
    }
  }

  // Initialize
  loadSounds()

  return {
    play,
    startBackgroundMusic,
    pauseBackgroundMusic,
    resumeBackgroundMusic,
    setMuted,
    isMuted: () => isMuted
  }
}

