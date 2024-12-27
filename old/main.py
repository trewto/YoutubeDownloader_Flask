from flask import Flask, render_template, request, Response
import yt_dlp
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    download_links = []

    if request.method == 'POST':
        link = request.form['link']

        # yt-dlp options for best quality video
        ydl_opts = {
            'format': 'best',
            'quiet': False  # Suppress console output
        }

        # Check if the link is a playlist or a single video
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # If the link is a playlist, extract all video links
                if 'playlist' in link:
                    playlist_dict = ydl.extract_info(link, download=False)
                    for video in playlist_dict['entries']:
                        download_links.append({
                            'title': video.get('title', 'Video'),
                            'url': video.get('url', None)
                        })
                        print("process///+")
                else:
                    # If it's a single video, extract the link as usual
                    info_dict = ydl.extract_info(link, download=False)
                    download_links.append({
                        'title': info_dict.get('title', 'Video'),
                        'url': info_dict.get('url', None)
                    })
        except Exception as e:
            download_links = [{'title': f"Error: {str(e)}", 'url': None}]

    return render_template('index.html', download_links=download_links)


@app.route('/download')
def download():
    video_url = request.args.get('url')
    title = request.args.get('title', 'video')

    head_response = requests.head(video_url)
    file_size = head_response.headers.get('Content-Length', 0)

    # Fetch the video stream from the URL
    def generate():
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

    # Serve the video with the specified filename
    response = Response(generate(), content_type="video/mp4")
    response.headers['Content-Disposition'] = f'attachment; filename="{title}.mp4"'
    response.headers['Content-Length'] = file_size  # Add file size to headers
    return response

if __name__ == '__main__':
    app.run(debug=True)
