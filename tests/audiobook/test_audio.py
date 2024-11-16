from audiobook.audio import AudioManager


def test_audio_initialization(audio_file_path):
    """Test AudioManager initialization."""
    audio_manager = AudioManager(audio_file_path)
    assert audio_manager.audio_path == audio_file_path
    assert not audio_manager.audio_chunks  # Should start empty


def test_get_audio_chunk(audio_file_path, sample_subtitle):
    """Test getting an audio chunk."""
    audio_manager = AudioManager(audio_file_path)
    chunk = audio_manager.get_chunk(sample_subtitle)

    assert chunk is not None
    assert isinstance(chunk, bytes)
    assert len(chunk) > 0


def test_audio_caching(audio_file_path, sample_subtitle):
    """Test that audio chunks are properly cached."""
    audio_manager = AudioManager(audio_file_path)

    # Get chunk first time
    first_chunk = audio_manager.get_chunk(sample_subtitle)
    assert sample_subtitle.index in audio_manager.audio_chunks

    # Get same chunk again
    second_chunk = audio_manager.get_chunk(sample_subtitle)
    assert first_chunk == second_chunk  # Should return cached version


def test_clear_cache(audio_file_path, sample_subtitle):
    """Test cache clearing."""
    audio_manager = AudioManager(audio_file_path)
    audio_manager.get_chunk(sample_subtitle)
    assert len(audio_manager.audio_chunks) > 0

    audio_manager.clear_cache()
    assert len(audio_manager.audio_chunks) == 0


def test_preload_chunks(audio_file_path, subtitles):
    """Test preloading multiple chunks."""
    audio_manager = AudioManager(audio_file_path)
    first_three_subtitles = subtitles.subtitles_list[:3]

    audio_manager.preload_chunks(first_three_subtitles)
    assert len(audio_manager.audio_chunks) == 3

    # Verify all chunks are valid
    for subtitle in first_three_subtitles:
        chunk = audio_manager.audio_chunks[subtitle.index]
        assert isinstance(chunk, bytes)
        assert len(chunk) > 0
