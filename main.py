from dotenv import load_dotenv

load_dotenv()
import gradio as gr
from src.utils import process_image_and_solve_with_progress, process_image_and_augment_questions

def solve_with_progress(image, enable_multi_model, selected_models, progress=gr.Progress(), lecturing_methods="Demonstration", characteristic="enthusiastic and encouraging"):
    """Wrapper function to show progress during solving"""
    if image is None:
        yield "Please upload an image first.", {}, ""
    
    progress(0.1, desc="Processing image...")
    try:
        result = process_image_and_solve_with_progress(image, enable_multi_model, selected_models, progress, lecturing_methods, characteristic)
        for i in result:
            yield i
    except Exception as e:
        yield f"Error: {str(e)}", {}, ""

# Custom CSS for better styling
custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto;
}
.title {
    text-align: center;
    color: #2563eb;
    margin-bottom: 20px;
}
.output-box {
    min-height: 200px;
}
"""

with gr.Blocks(css=custom_css, title="STEMMate") as demo:
    gr.Markdown("# 🧮 STEMMate", elem_classes=["title"])

    with gr.Tabs():
        with gr.Tab("Question generator"):
            with gr.Column():
                image_input = gr.Image(type="pil", label="Upload Image", height=400)
                num_questions_slider = gr.Slider(1, 5, value=3, step=1, label="Number of Questions to Generate")
                generate_btn = gr.Button("Generate Question", variant="primary", size="lg")
                question_output = gr.Markdown(
                    label="Generated Question",
                    elem_classes=["output-box"],
                    show_copy_button=True,
                    container = True,
                    latex_delimiters=[
                        { "left": "$$", "right": "$$", "display": True }, 
                        { "left": "$", "right": "$", "display": False }
                    ]
                )

                generate_btn.click(
                    fn=process_image_and_augment_questions,  # Placeholder function
                    inputs=[image_input, num_questions_slider],
                    outputs=[question_output]
                )
        with gr.Tab("📚 Solver"):
            gr.Markdown("Upload an image containing a math question and get step-by-step solutions from multiple AI models.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## 📸 Input")
                    image_input = gr.Image(
                        type="pil", 
                        label="Upload Math Question Image",
                        height=400
                    )
                    
                    # Configuration options
                    with gr.Accordion("⚙️ Settings", open=True):
                        enable_multi_model = gr.Checkbox(
                            label="Enable Multi-Model Consensus", 
                            value=True,
                            info="Use multiple models for better accuracy"
                        )
                        selected_models = gr.CheckboxGroup(
                            choices=[
                                "Qwen/Qwen3-Next-80B-A3B-Thinking",
                                "Qwen/Qwen3-235B-A22B-fp8-tput", 
                                "openai/gpt-oss-20b"
                            ],
                            value=[
                                "Qwen/Qwen3-Next-80B-A3B-Thinking",
                            ],
                            label="Select Models to Use",
                            info="Choose which models to use for solving"
                        )
                        lecturing_methods = gr.Dropdown(
                            choices=[
                                "Lecture/Direct Instruction",
                                "Socratic/Questioning",
                                "Demonstration",
                            ],
                            value="Lecture/Direct Instruction",
                            label="Explanation Style",
                            info="Choose the style of explanation for the solution"
                        )
                        characteristic = gr.Dropdown(
                            choices=[
                                "Mr. Rogers",
                                "The Genie from Aladdin",
                                "Dumbledore",
                                "Doraemon",
                                "Hermione Granger",
                                "Sherlock Holmes",
                                "Yoda",
                                "Winnie the Pooh",
                                "Baymax",
                                "Tony Stark",
                                "Mulan",
                                "Albert Einstein",
                                "SpongeBob SquarePants"
                            ],
                            value="Yoda",
                            label="Tutor Characteristic",
                            info="Choose the characteristic of the tutor"
                        )
                    
                    solve_btn = gr.Button("🚀 Solve Question", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ Clear All", variant="secondary")
                    
                with gr.Column(scale=2):
                    gr.Markdown("## 📝 Results")
                    
                    with gr.Tabs():
                        with gr.Tab("📋 Summary"):
                            question_output = gr.Markdown(
                                label="Extracted Question",
                                # lines=3,
                                elem_classes=["output-box"],
                                show_copy_button=True,
                                container = True,
                                latex_delimiters=[
                                    { "left": "$$", "right": "$$", "display": True }, 
                                    { "left": "$", "right": "$", "display": False }
                                ],
                            )
                            answer_output = gr.Textbox(
                                label="Final Answer",
                                lines=2,
                                elem_classes=["output-box"],
                                show_copy_button=True
                            )
                            
                        with gr.Tab("🔍 Detailed Steps"):
                            steps_output = gr.Markdown(
                                label="Solution Steps by Model",
                                elem_classes=["output-box"],
                                container = True,
                                latex_delimiters=[
                                    { "left": "$$", "right": "$$", "display": True }, 
                                    { "left": "$", "right": "$", "display": False }
                                ],
                            )
                        with gr.Tab("🧑‍🏫 Explanation"):
                            explanation_output = gr.Markdown(
                                label="Personalized Explanation",
                                elem_classes=["output-box"],
                                container = True,
                                latex_delimiters=[
                                    { "left": "$$", "right": "$$", "display": True }, 
                                    { "left": "$", "right": "$", "display": False }
                                ],
                            )
                        
                        with gr.Tab("📊 Model Comparison"):
                            model_comparison = gr.Dataframe(
                                headers=["Model", "Answer", "Confidence"],
                                label="Model Results Comparison",
                                elem_classes=["output-box"]
                            )
            
            # Event handlers
            solve_btn.click(
                fn=solve_with_progress,
                inputs=[image_input, enable_multi_model, selected_models, lecturing_methods, characteristic],
                outputs=[question_output, steps_output, answer_output, explanation_output],
                show_progress=True
            )
            
            clear_btn.click(
                fn=lambda: (None, "", {}, "", "", []),
                outputs=[image_input, question_output, steps_output, answer_output, explanation_output, model_comparison]
            )

            gr.Markdown(
"""## 💡 Tips
- Upload clear images with readable text
- Enable multi-model consensus for better accuracy
- Check the detailed steps tab for complete solutions
- Use the settings to customize which models to use
""")

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )