# Audio Converter (Windows Only, for now)

A simple desktop application built with Python and Tkinter to convert audio and video files into various audio formats. It supports both single-file and batch conversions using the power of FFmpeg.



## Key Features

* **Dual Conversion Modes**: Choose between converting a single file or processing multiple files in a batch.
* **Wide Format Support**: Convert to popular formats like MP3, WAV, FLAC, AAC, OGG, M4A, and WMA.
* **Quality Control**: Adjust the audio quality (bitrate) for supported formats.
* **Intuitive Interface**: A user-friendly GUI with a progress bar and a detailed process log.
* **FFmpeg Validation**: Automatically checks if FFmpeg is installed and accessible.
* **Open Source**: Free to use, modify, and distribute.

## Getting Started (for Users)

1.  **Download the latest release** from the [Releases Page here](https://github.com/USERNAME/REPOSITORY_NAME/releases).
2.  **Choose your version**:
    * **`audio-converter-with-ffmpeg` (Recommended)**: This version is portable and includes everything you need to run the application.
    * **`audio-converter-only`**: Use this only if you are an advanced user and have already installed FFmpeg on your system.
3.  Unzip the downloaded file and double-click `audio-converter.exe` to run the application.

## For Developers (Running from Source)

If you want to modify or run the application from its source code, follow these steps:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/andrr64/audio-converter-with-ffmpeg.git
    cd audio-converter-with-ffmpeg
    ```
2.  **Set up FFmpeg**:
    * Download FFmpeg from the [official website](https://ffmpeg.org/download.html).
    * Ensure the `ffmpeg.exe` executable is placed inside a `./ffmpeg/bin/` folder, or add its location to your system's PATH.
3.  **Run the Application**:
    ```bash
    python app.py
    ```

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

In short, you are free to:
* Use the software for any purpose (commercial or personal).
* Modify the software to suit your needs.
* Redistribute the software.

The only condition is that you include the original copyright and license notice in any copy of the software.

---

Created by **Derza Andreas** with AI assistance.

