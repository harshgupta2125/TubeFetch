from pathlib import Path
import shutil

import streamlit as st

import downloader_funcs as df


st.set_page_config(page_title="TubeFetch", layout="wide")

top_left, top_right = st.columns([1, 1])
with top_left:
	st.markdown("### TubeFetch")
with top_right:
	st.markdown(
		"<div style='text-align:right'>"
		"<a href='https://github.com/harshgupta2125' target='_blank' style='text-decoration:none'>GitHub</a>"
		"</div>",
		unsafe_allow_html=True,
	)

st.markdown("# YouTube **Video & Playlist** Downloader")
st.caption("Local project for personal backups. Respect creators and copyright.")

st.info(
	"⚠️ Public Demo Mode: Downloads limited to 10 mins & 5 playlist items to save resources. Clone the repo and disable demo mode for full use.",
	icon="⚠️",
)

url = st.text_input(
	"Paste video or playlist link here...",
	placeholder="https://youtube.com/playlist/videos?...",
)

col_input, col_button = st.columns([4, 1])
with col_input:
	output_dir = st.text_input("Save to folder", value=str(Path.home() / "Downloads"))
with col_button:
	start_clicked = st.button("Fetch", use_container_width=True)

toggle_row = st.columns([1.2, 1.2, 1])
with toggle_row[0]:
	format_choice = st.radio("Format", ("MP3", "MP4"), horizontal=True)
with toggle_row[1]:
	mode = st.radio("What", ("Playlist", "Single video"), horizontal=True)
with toggle_row[2]:
	zip_playlist = st.checkbox("Zip Playlist", value=True)

with st.expander("More options"):
	album_mode = st.checkbox(
		"Album Mode (audio): embed cover art and metadata",
		value=True,
		help="Adds thumbnail as album art and writes tags when downloading audio.",
	)
	subtitle_mode_value = "off"
	if format_choice == "MP4":
		subtitle_choice = st.radio(
			"Subtitles",
			(
				"No subtitles",
				"Embed (soft, keeps file size small)",
				"Burn into video (always visible)",
			),
		)
		subtitle_mode_value = {
			"No subtitles": "off",
			"Embed (soft, keeps file size small)": "embed",
			"Burn into video (always visible)": "burn",
		}.get(subtitle_choice, "off")
	else:
		subtitle_mode_value = "off"

if start_clicked:
	with st.spinner("Fetching and downloading..."):
		try:
			audio_only = format_choice == "MP3"
			if mode == "Playlist":
				files = df.download_playlist(
					url,
					output_dir,
					audio_only=audio_only,
					album_mode=album_mode and audio_only,
					subtitle_mode=subtitle_mode_value,
				)
				zip_path = None
				if zip_playlist and files:
					playlist_dir = Path(files[0]).parent
					zip_base = playlist_dir.parent / playlist_dir.name
					zip_path = shutil.make_archive(str(zip_base), "zip", root_dir=playlist_dir)
				if zip_path:
					st.success(f"Downloaded {len(files)} items and zipped to {zip_path}")
				else:
					st.success(f"Downloaded {len(files)} items to {Path(output_dir).expanduser()}")
			else:
				filepath = df.download_video(
					url,
					output_dir,
					audio_only=audio_only,
					album_mode=album_mode and audio_only,
					subtitle_mode=subtitle_mode_value,
				)
				st.success(f"Saved to {filepath}")
		except df.DownloadError as err:
			st.error(str(err))
		except Exception as err:
			st.error(f"Unexpected error: {err}")

st.divider()

st.markdown("**How to use**")
steps = st.columns(3)
steps[0].markdown("1. Paste link")
steps[1].markdown("2. Select format")
steps[2].markdown("3. Click Fetch")

st.markdown(
	"<div style='margin-top:12px'>🛡️ No-Logs: We do not store history or files. Server clears every 10 mins. This local build is not hosted publicly.</div>",
	unsafe_allow_html=True,
)

st.markdown("---")
footer_cols = st.columns([1, 1, 1, 1])
footer_cols[0].markdown("[DMCA / Copyright](#)")
footer_cols[1].markdown("[Terms of Service](#)")
footer_cols[2].markdown("[Contact](mailto:harsh2125gupta@gmail.com)")
footer_cols[3].markdown("Status: 🟢 Local Project (not live)")
