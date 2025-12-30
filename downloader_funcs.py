import os
from pathlib import Path
import shutil
import subprocess
from typing import List, Optional

import yt_dlp as ytdl


class DownloadError(Exception):
    """Raised when a download cannot be completed."""


DEMO_MODE = os.getenv("TUBEFETCH_DEMO_MODE", "1") != "0"
DEMO_MAX_PLAYLIST_ITEMS = int(os.getenv("TUBEFETCH_DEMO_MAX_ITEMS", "5"))
DEMO_MAX_DURATION_SECONDS = int(os.getenv("TUBEFETCH_DEMO_MAX_DURATION", "600"))
MAX_VIDEO_HEIGHT = int(os.getenv("TUBEFETCH_MAX_HEIGHT", "1080"))


def _ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise DownloadError("ffmpeg is required but was not found on PATH. Install ffmpeg and retry.")


def _build_opts(target_dir: Path, audio_only: bool, playlist: bool, album_mode: bool, subtitle_mode: str) -> dict:
    if audio_only:
        fmt = "bestaudio/best"
    else:
        fmt = f"bestvideo[height<={MAX_VIDEO_HEIGHT}]+bestaudio/best[height<={MAX_VIDEO_HEIGHT}]"
    template = "%(title)s.%(ext)s"
    if playlist:
        template = "%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"

    postprocessors = []
    if audio_only:
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        )
        if album_mode:
            postprocessors.append({"key": "EmbedThumbnail"})
            postprocessors.append({"key": "AddMetadata"})
    else:
        subs_on = subtitle_mode != "off"
        if subs_on:
            # Convert to srt for broader device support; yt-dlp will download auto subs if available.
            postprocessors.append({"key": "FFmpegSubtitlesConvertor", "format": "srt"})
            if subtitle_mode == "embed":
                postprocessors.append({"key": "FFmpegEmbedSubtitle"})
        postprocessors.append(
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        )

    opts = {
        "format": fmt,
        "outtmpl": str(target_dir / template),
        "noplaylist": not playlist,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4" if not audio_only else "mp3",
        "postprocessors": postprocessors,
        "ignoreerrors": True,  # keep going even if one video fails
        "writethumbnail": audio_only and album_mode,
    }

    if DEMO_MODE and playlist:
        opts["playlistend"] = DEMO_MAX_PLAYLIST_ITEMS

    if not audio_only and subtitle_mode != "off":
        opts.update(
            {
                "writesubtitles": True,
                "writeautomaticsub": True,
                "embedsubtitles": subtitle_mode == "embed",
                "subtitleslangs": ["en", "en.*", "en-US", "en-GB", "und", ""],
                "subtitlesformat": "srt/best",
            }
        )

    return opts


def _collect_filepaths(info: dict, ydl: ytdl.YoutubeDL) -> List[str]:
    files: List[str] = []

    requested = info.get("requested_downloads") or []
    for item in requested:
        path = item.get("filepath") or item.get("filename")
        if path:
            files.append(path)

    if not files and info.get("entries"):
        for entry in info["entries"] or []:
            if not entry:
                continue
            path = entry.get("filepath") or entry.get("filename")
            if not path:
                path = ydl.prepare_filename(entry)
            if path:
                files.append(path)

    if not files:
        path = info.get("filepath") or info.get("filename")
        if not path:
            path = ydl.prepare_filename(info)
        if path:
            files.append(path)

    return files


def _find_subtitle_file(video_path: Path) -> Optional[Path]:
    stem = video_path.with_suffix("").name
    parent = video_path.parent
    candidates = [
        parent / f"{stem}.en.srt",
        parent / f"{stem}.srt",
        parent / f"{stem}.en.vtt",
        parent / f"{stem}.vtt",
    ]
    for cand in candidates:
        if cand.exists():
            return cand
    return None


def _burn_subtitles(video_path: Path, subtitle_path: Path) -> Path:
    burned_path = video_path.with_name(f"{video_path.stem}.subbed{video_path.suffix}")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"subtitles={subtitle_path.as_posix()}",
        "-c:a",
        "copy",
        str(burned_path),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise DownloadError(f"Failed to burn subtitles: {exc.stderr.decode(errors='ignore')[:500]}") from exc
    return burned_path


def _download(url: str, output_dir: str, audio_only: bool, playlist: bool, album_mode: bool, subtitle_mode: str) -> List[str]:
    if not url:
        raise DownloadError("A video URL is required.")

    _ensure_ffmpeg()

    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = _build_opts(target_dir, audio_only, playlist, album_mode, subtitle_mode)

    # Preview to enforce demo limits without partially downloading.
    preview_opts = {**ydl_opts, "skip_download": True}
    with ytdl.YoutubeDL(preview_opts) as ydl_preview:
        info_preview = ydl_preview.extract_info(url, download=False)

    if DEMO_MODE and not audio_only:
        def _duration_exceeds(duration: Optional[int]) -> bool:
            return duration is not None and duration > DEMO_MAX_DURATION_SECONDS

        if playlist and info_preview.get("entries"):
            for entry in info_preview["entries"][:DEMO_MAX_PLAYLIST_ITEMS]:
                if not entry:
                    continue
                if _duration_exceeds(entry.get("duration")):
                    raise DownloadError(
                        f"Blocked in demo mode: {entry.get('title', 'video')} exceeds {DEMO_MAX_DURATION_SECONDS // 60} minutes."
                    )
        else:
            if _duration_exceeds(info_preview.get("duration")):
                raise DownloadError(
                    f"Blocked in demo mode: videos over {DEMO_MAX_DURATION_SECONDS // 60} minutes are disabled."
                )

    try:
        with ytdl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            files = _collect_filepaths(info, ydl)
    except Exception as exc:  # yt_dlp raises many exception types
        raise DownloadError(f"Download failed: {exc}") from exc

    if not files:
        raise DownloadError("No files were downloaded.")

    # Optional hard-burn subtitles after download (video only).
    if not audio_only and subtitle_mode == "burn":
        burned_files: List[str] = []
        for f in files:
            video_path = Path(f)
            sub_file = _find_subtitle_file(video_path)
            if not sub_file:
                raise DownloadError(f"Subtitle file not found to burn for {video_path.name}")
            burned = _burn_subtitles(video_path, sub_file)
            burned_files.append(str(burned))
        return burned_files

    return files


def download_video(
    url: str,
    output_dir: str,
    audio_only: bool = False,
    album_mode: bool = False,
    subtitle_mode: str = "off",
) -> str:
    """Download a single YouTube video to the given directory."""

    files = _download(
        url,
        output_dir,
        audio_only,
        playlist=False,
        album_mode=album_mode,
        subtitle_mode=subtitle_mode,
    )
    return files[0]


def download_playlist(
    url: str,
    output_dir: str,
    audio_only: bool = False,
    album_mode: bool = False,
    subtitle_mode: str = "off",
) -> List[str]:
    """Download an entire playlist in one click.

    Returns all downloaded file paths.
    """

    return _download(
        url,
        output_dir,
        audio_only,
        playlist=True,
        album_mode=album_mode,
        subtitle_mode=subtitle_mode,
    )
