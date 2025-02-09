# Video Summarization Proof of Concept

This repository contains a proof-of-concept application for summarizing videos using a combination of audio extraction, speech recognition, and text summarization.

## Project Overview

This project aims to demonstrate the feasibility of automatically generating concise summaries of various types of videos. It leverages the power of OpenAI's Whisper for speech recognition and utilizes the Gemma 2 27B model for text summarization.

## Installation and Usage

Before installing make sure you have [`conda`](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#installing-conda) in your system.

To install this repo and use the summarizer:

```bash
git clone git@github.com:lfenzo/video-summarization-poc.git
cd video-summarization-poc
bash -l setup.sh 
```

To get the video summary, pass your YouTube URL to `summarize.py` python script and optionally provide a summary file name with `--output`/`-o`:

```bash
python summarize.py <URL> -o my_summary.txt
```

> [!TIP]
> Even though both transcription and summarization can be run on CPU, we recommend checking the VRAM requirements to tune the model size (Whisper) and the number of layers offloaded to the GPU and context length (Gemma) to make the most out of your hardware.
>
> To do so, you can change the `--model-size`, to adjust the Whisper model size, the `--n-gpu-layers`, to control the number of layers offloaded to the GPU during inference, and `--n-ctx` to change the context length:
>
> ```bash
> python summarize.py <URL> -o my_summary.txt \
>     --model-size base \
>     --n-gpu-layers 10 \
>     --n-ctx 2048
> ```
> 
> For more information:
>
> ```
> python summarize.py --help 
> ```

### Video Categories

The project focuses on three distinct categories of videos:

- **Short Videos:** Concise clips with a limited duration (e.g., social media snippets, trailers).
- **Medium-Sized Videos:** Videos with a moderate length, ranging from 10 to 25 minutes (e.g., educational content, online lectures).
- **Long Videos:** Extensive recordings, typically lasting between 1 and 2 hours (e.g., university lectures, conference presentations).

### Technology Stack

- Audio Extraction: [`pytube`](https://github.com/pytube/pytube) and [`pydub`](https://github.com/jiaaro/pydub).
- Speech Recognition: [OpenAI Whisper](https://openai.com/blog/whisper/)
- Text Summarization: [Gemma 2 27B](https://huggingface.co/google/gemma-2-27b)

## Computation Cost Analysis

A computational cost analysis has been conducted to evaluate the VRAM requirements, execution times, and performance of the Whisper model on both GPU and CPU. For detailed findings and methodology, please refer to the [Transcription README.](./transcription/README.md).

## Future Work and Contributions

This is a proof-of-concept project, and there are several opportunities for expansion:

- **Video Segmentation:** Implementing techniques to segment videos into meaningful units for more accurate summarization.
- **Summary Customization:** Providing options for users to control the length and style of the generated summaries.
- **User Interface:** Developing a user-friendly interface for interacting with the system.

Feel free to explore the code, experiment with the summaries, and contribute to the project's development!
