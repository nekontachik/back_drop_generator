"""Audio analysis endpoint — analyze uploaded audio and suggest a visual prompt."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.models.audio import AudioAnalysis
from app.services.audio_analyzer import analyze_audio, validate_audio

router = APIRouter()


class AnalyzeResponse(BaseModel):
    """Response from audio analysis with a suggested visual prompt."""

    analysis: AudioAnalysis
    suggested_prompt: str


def _build_prompt_from_analysis(analysis: AudioAnalysis) -> str:
    """Generate a descriptive visual prompt from audio features.

    Maps mood labels and BPM to a creative text description that
    the RAG pipeline can match against genre documents.
    """
    labels = analysis.mood.labels  # ["bright"/"dark", "energetic"/"mellow", "dense"/"sparse"]
    bpm = analysis.bpm.detected

    # Brightness → visual tone
    brightness = labels[0] if len(labels) > 0 else "dark"
    energy = labels[1] if len(labels) > 1 else "mellow"
    density = labels[2] if len(labels) > 2 else "sparse"

    # Map mood to visual descriptors
    tone_map = {
        ("bright", "energetic"): "Vivid neon bursts and electric color explosions",
        ("bright", "mellow"): "Soft luminous gradients with gentle floating particles",
        ("dark", "energetic"): "Deep pulsing shadows with sharp geometric flashes",
        ("dark", "mellow"): "Ethereal dark atmosphere with slowly drifting nebula forms",
    }
    tone = tone_map.get((brightness, energy), "Abstract visual patterns")

    # Density → visual complexity
    complexity = (
        "intricate layered detail and rapid motion"
        if density == "dense"
        else "clean minimal shapes with breathing space"
    )

    # BPM → tempo feel
    if bpm >= 140:
        tempo_feel = "high-energy fast-paced"
    elif bpm >= 120:
        tempo_feel = "driving rhythmic"
    elif bpm >= 90:
        tempo_feel = "mid-tempo groovy"
    else:
        tempo_feel = "slow atmospheric"

    # Spectral centroid → color temperature hint
    centroid = analysis.mood.spectral_centroid
    color_hint = (
        "cool cyan and blue tones"
        if centroid < 2000
        else "warm amber and violet hues"
        if centroid > 3500
        else "balanced color spectrum"
    )

    return (
        f"{tone}, {complexity}. "
        f"{tempo_feel.capitalize()} at {bpm} BPM with {color_hint}. "
        f"Synced to the beat, reactive and immersive."
    )


@router.post("/analyze-audio", response_model=AnalyzeResponse)
async def analyze_audio_endpoint(
    audio: UploadFile = File(...),
) -> AnalyzeResponse:
    """Analyze an uploaded audio file and return features + suggested prompt.

    Runs librosa BPM detection and mood analysis, then generates a
    descriptive visual prompt from the extracted features.
    """
    audio_bytes = await audio.read()

    try:
        validate_audio(audio_bytes, audio.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        analysis = await asyncio.to_thread(analyze_audio, audio_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=422, detail=f"Audio analysis failed: {exc}"
        )

    suggested_prompt = _build_prompt_from_analysis(analysis)

    return AnalyzeResponse(
        analysis=analysis,
        suggested_prompt=suggested_prompt,
    )
