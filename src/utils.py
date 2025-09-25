from src.services import image_parser, solver, personalized_explanation, question_generator
import numpy as np
from collections import Counter



from PIL import Image
import base64
import io


model_queue = [
    # "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    "Qwen/Qwen3-235B-A22B-fp8-tput",
    "Qwen/Qwen3-Next-80B-A3B-Thinking",
    "openai/gpt-oss-20b"
]
def process_image_and_solve(image) -> dict:
    """
    Process the image from the given URL, extract the question, and solve it using multiple models.
    Args:
        image_url (str): URL of the image containing the question.
    Returns:
        dict: A dictionary containing the question, steps, and final answer.
    """
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()
    image_str = base64.b64encode(image_bytes).decode('utf-8')
    question = image_parser(
        image_str, 
        model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    )
    print(f"Extracted question: {question}")

    answer = None
    solutions = []
    model_idx=0
    while True:
        solution = solver(question, model = model_queue[model_idx])
        solutions.append(solution)
        print(f"Model {model_queue[model_idx]} produced solution: {solution}")
        unique_answers = Counter([sol.get("answer", "") for sol in solutions])
        unique_answers = list(unique_answers.items())
        if unique_answers[0][1]>1:
            answer = unique_answers[0][0]
            break

        model_idx += 1
        if model_idx >= len(model_queue):
            break
    if answer is None:
        answer = solutions[0].get("answer", "").strip()
    
    final_steps = {}
    for idx, sol in enumerate(solutions):
        final_steps[f"Model_{model_queue[idx]}"] = sol.get("steps", [])
    # for idx, sol in enemuate(solutions):
    #     if i.get("answer", "") == answer:
    #         final_steps[f""] = i.get("steps", [])
    #         break

    return  question, final_steps, answer




def process_image_and_solve_with_progress(image, enable_multi_model=True, selected_models=None, progress=None, lecturing_methods="" , characteristic="") -> tuple:
    """
    Process the image from the given URL, extract the question, and solve it using multiple models.
    Args:
        image: PIL Image containing the question.
        enable_multi_model (bool): Whether to use multiple models for consensus.
        selected_models (list): List of models to use.
        progress: Gradio progress tracker.
    Returns:
        tuple: A tuple containing the question, steps, and final answer.
    """
    if progress:
        progress(0.2, desc="Converting image...")
    
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()
    image_str = base64.b64encode(image_bytes).decode('utf-8')
    
    if progress:
        progress(0.4, desc="Extracting question...")
    
    question = image_parser(
        image_str, 
        model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    )
    print(f"Extracted question: {question}")

    yield question, "", "", ""

    # Use selected models or default queue
    active_models = selected_models if selected_models else model_queue
    
    if not enable_multi_model:
        active_models = active_models[:1]  # Use only first model
    
    if progress:
        progress(0.6, desc="Solving with AI models...")

    answer = None
    solutions = []
    
    for idx, model in enumerate(active_models):
        if progress:
            progress(0.6 + 0.3 * (idx + 1) / len(active_models), desc=f"Using {model.split('/')[-1]}...")
        
        solution = solver(question, model=model)

        
        temp_steps= {model.split('/')[-1]: solution.get("steps", [])}
        temp_markdown = "===".join([f"### Steps from {k}\n\n" + "\n\n".join(v) for k, v in temp_steps.items()])
        print(f"Model {model} produced solution: {temp_markdown}")
        yield question, temp_markdown, "Temporary answer: " + solution.get("answer", "").strip(), ""

        temp_explanation = personalized_explanation(
            question, 
            solution, 
            lecturing_methods, 
            characteristic,
            model="google/gemma-3n-E4B-it"
        )
        solution["explanation"] = temp_explanation

        print(f"Personalized explanation: {temp_explanation}")
         
        solutions.append(solution)

        yield question, temp_markdown, "Temporary answer: " + solution.get("answer", "").strip(), temp_explanation
        
        if enable_multi_model:
            unique_answers = Counter([sol.get("answer", "") for sol in solutions])
            unique_answers = list(unique_answers.items())
            if len(unique_answers) > 0 and unique_answers[0][1] > 1:
                answer = unique_answers[0][0]
                break
        else:
            answer = solution.get("answer", "").strip()
            break
    
    if answer is None and solutions:
        answer = solutions[0].get("answer", "").strip()
    
    final_steps = {}
    for idx, sol in enumerate(solutions):
        model_name = active_models[idx].split('/')[-1] if idx < len(active_models) else f"Model_{idx}"
        final_steps[model_name] = sol.get("steps", [])

    if progress:
        progress(1.0, desc="Complete!")

    final_markdown = "\n\n===\n\n".join([f"### Steps from {k}\n\n" + "\n\n".join(v) for k, v in final_steps.items()])
    final_explanation = "\n\n".join([f"### Explanation from {active_models[idx].split('/')[-1] if idx < len(active_models) else f'Model_{idx}'}\n\n" + sol.get("explanation", "") for idx, sol in enumerate(solutions)])
    yield question, final_markdown, answer, final_explanation
    # return question, final_steps, answer


def process_image_and_augment_questions(image, num_augmented=3) -> tuple:
    """
    Process the image from the given URL, extract the question, and generate augmented questions.
    Args:
        image: PIL Image containing the question.
        num_augmented (int): Number of augmented questions to generate.
    Returns:
        tuple: A tuple containing the original question and a list of augmented questions.
    """
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()
    image_str = base64.b64encode(image_bytes).decode('utf-8')
    
    question = image_parser(
        image_str, 
        model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    )
    print(f"Extracted question: {question}")

    questions_str = question_generator(
        question, 
        num_question=num_augmented,
        model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    )
    # augmented_questions = [q.strip() for q in questions_str.split("## Question") if q.strip()]
    
    return questions_str