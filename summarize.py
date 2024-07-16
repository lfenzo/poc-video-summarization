import gc
import os
import logging
from argparse import ArgumentParser

import torch
import whisper
from llama_cpp import Llama
from pytubefix import YouTube
from pydub import AudioSegment

N_CTX = 8_192
N_GPU_LAYERS = 29


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='summarizer.log',
)


def free_gpu_memory_after_call(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        finally:
            gc.collect()
            del args, kwargs
            torch.cuda.empty_cache()
        return result
    return wrapper


def write_text_file(content: str, filepath: str | os.PathLike) -> None:
    with open(filepath, 'w') as file:
        file.write(content)


def get_audio_from_youtube_video(url: str, output_filename: str, fmt: str = 'mp3') -> None:
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    downloaded_file = video.download()

    output_file = f"{output_filename}.{fmt}"
    audio = AudioSegment.from_file(downloaded_file)
    audio.export(output_file, format=fmt)

    os.remove(downloaded_file)
    return output_file


@free_gpu_memory_after_call
def transcribe_audio(audio_file: str | os.PathLike, model_size: str = "large") -> str:
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_file)
    return result['text']


@free_gpu_memory_after_call
def summarize_text(text: str, n_gpu_layers: int, n_ctx: int) -> str:
    model = Llama.from_pretrained(
        repo_id="bartowski/gemma-2-27b-it-GGUF",
        filename="gemma-2-27b-it-Q5_K_L.gguf",
        n_gpu_layers=n_gpu_layers,
        n_ctx=n_ctx,
        verbose=True,
    )
    response = model.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": f"""
                    Please, summarize the following text using bullet points: {text}
                    The produced text must be in the same language as the original!
                    You may add details and complement some information when appropriate.
                    """
            }
        ],
    )
    return response['choices'][0]['message']['content']


def define_cli_args():
    parser = ArgumentParser(description='Summarize YouTube videos.')
    parser.add_argument('url', type=str, help='YouTube video URL')
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='summary.txt',
        help='Path to the output file where the summary will be saved.'
    )
    parser.add_argument(
        '-m', '--model-size',
        type=str,
        default='large',
        choices=['tiny', 'small', 'medium', 'large', 'base'],
        help='Whisper model size for transcription (default: large)'
    )
    parser.add_argument(
        '--n-gpu-layers',
        type=int,
        default=N_GPU_LAYERS,
        help='Number of model layers to be offloaded to GPU during summarization (default: 29)'
    )
    parser.add_argument(
        '--n-ctx',
        type=int,
        default=N_CTX,
        help='Context size for Gemma summarization (default: 8192)'
    )
    return vars(parser.parse_args())


if __name__ == "__main__":
    args = define_cli_args()

    logging.info(f"Doenloading audio from youtube video url={args['url']}")
    audio_file = get_audio_from_youtube_video(url=args['url'], output_filename='tmp_audio', fmt='mp3')

    logging.info(f"Transcribing audio in file {audio_file}...")
    transcription = transcribe_audio(audio_file, model_size=args['model_size'])

    logging.info(f'Summarizing transcription with {args['n_gpu_layers']} GPU layers...')
    summary = summarize_text(transcription, n_gpu_layers=args['n_gpu_layers'], n_ctx=args['n_ctx'])

    logging.info(f"Saving summary to text file {args['output']}")
    write_text_file(summary, filepath=args['output'])
