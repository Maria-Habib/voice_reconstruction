

import gradio as gr
import json
import os

# Load the precomputed JSON
with open("precomputed_ASR_TTS_uclass1.json", "r") as f:
    data = json.load(f)

# Convert to list for indexing
keys = list(data.keys())
total = len(keys)

# To store annotations
annotations = {}

def display_sample(index):
    key = keys[index]
    entry = data[key]
    transcription = entry["transcription"]
    original_audio_path = key
    tts_audio_path = entry["tts_audio"]
    return (
        f"{index+1}/{total}", 
        original_audio_path, 
        transcription, 
        tts_audio_path
    )

def annotate(index, label):
    key = keys[index]
    annotations[key] = label
    index = (index + 1) % total
    return (*display_sample(index), index)

def go_to_page(page_input):
    try:
        page = int(page_input.strip()) - 1
        if page < 0 or page >= total:
            raise ValueError
    except:
        return gr.update(value="Invalid page"), *display_sample(0), 0
    return gr.update(value=f"{page+1}/{total}"), *display_sample(page), page

with gr.Blocks() as demo:
    index_state = gr.State(0)

    with gr.Row():
        page_label = gr.Textbox(value="1/{}".format(total), label="Page", interactive=True)
        go_btn = gr.Button("Go")

    with gr.Row():
        original_audio = gr.Audio(label="Original Audio", type="filepath")
        tts_audio = gr.Audio(label="TTS Audio", type="filepath")

    transcription_text = gr.Textbox(label="Transcription", lines=4)

    with gr.Row():
        same_btn = gr.Button("✅ Same Speaker", variant="primary")
        diff_btn = gr.Button("❌ Different Speaker", variant="stop")

    same_btn.click(fn=annotate, inputs=[index_state, gr.Textbox(value="same", visible=False)], 
                   outputs=[page_label, original_audio, transcription_text, tts_audio, index_state])
    diff_btn.click(fn=annotate, inputs=[index_state, gr.Textbox(value="different", visible=False)], 
                   outputs=[page_label, original_audio, transcription_text, tts_audio, index_state])
    go_btn.click(fn=go_to_page, inputs=page_label, 
                 outputs=[page_label, original_audio, transcription_text, tts_audio, index_state])

    # Load first sample
    demo.load(fn=display_sample, inputs=index_state, 
              outputs=[page_label, original_audio, transcription_text, tts_audio])

demo.launch()


