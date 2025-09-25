from openai import OpenAI
import os 

from PIL import Image

client = OpenAI(
    api_key= os.getenv("OPENAI_API_KEY"),
    base_url= os.getenv("OPENAI_API_BASE_URL")
)

def generate(
    prompt: str,
    model: str = "gpt-4o"
) -> str:
    """Generate a response from the given prompt using the specified model.
    Args:
        prompt (str): The input prompt.
        model (str): The model to use for generation.
    Returns:
        str: The generated response.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Generate thoroughly answer for given question."},
            {"role": "user", "content": prompt}
        ],
        max_tokens = 10000,
        reasoning_effort="low",
        top_p=0.7
    )
    return response.choices[0].message.content


def process_response(response: str) -> dict:
    """
    Process the response string to extract steps and final answer.
    Args:
        response (str): The response string from the model.
    Returns:
        dict: A dictionary containing the steps and final answer.
    """
    step_pattern = "## Step"
    answer_parttern = "## Final Answer:"
    steps = []
    current_step = ""
    answer = ""
    steps = []
    for i in response.split("\n"):
        if answer_parttern in i:
            answer = i.split(answer_parttern)[-1].strip() + "\n\n"
        elif step_pattern in i:
            if current_step.strip() != "":
                steps.append(current_step.strip())
            current_step = i.strip()+ "\n\n"
        else:
            current_step += i.strip() + "\n\n" 
    if current_step:
        steps.append(current_step.strip())
    return {
        "steps": steps,
        "answer": answer
    }

def solver(
    question: str,
    model: str = "gpt-4o"

) -> dict:
    """
    Solve the given question step-by-step using the specified model.
    Args:
        question (str): The question to be solved.
        model (str): The model to use for solving the question.
    Returns:
        dict: A dictionary containing the steps and final answer.
    """
    prompt = f"Solve the following problem step-by-step and provide the final answer:\n\n{question}"
    # response_template = """{{
    # "steps": [<list of solution steps, with calculation and reasoning>],
    # "answer": <final answer>
# }}"""
    response_template = """## Step 1: 
...
## Step 2:
...

## Final Answer: <final answer (number or choice only, no sign or text, e.g., if answer is 42, just write 42, if answer is choice B, just write B)>
    """
    response = generate(prompt + "\n\nResponse exactly like below template, say nothing else.\n" + response_template, model=model)
    print(f"Raw response from model {model}: {response}")
    if "</think>" in response:
        response = response.split("</think>")[-1].strip()

    return process_response(response)  # Using eval for simplicity; consider safer parsing in production


teaching_methods = {
    "Lecture/Direct Instruction": "Teacher explains the solution step by step in a clear, structured way.",
    "Socratic/Questioning": "Teacher guides the solution by asking targeted questions instead of giving direct answers.",
    "Problem-Based/Inquiry": "Teacher lets students try first, then explains by highlighting reasoning and connecting to the correct solution.",
    "Demonstration": "Teacher works through the solution while verbalizing thought processes and showing methods.",
    "Collaborative/Peer Teaching": "Teacher listens to student explanations and steps in to clarify or model the correct solution.",
    "Flipped Classroom": "Teacher reinforces the solution in class by clarifying misconceptions and deepening understanding of pre-learned steps."
}

chacteristics_examples = {
    "Mr. Rogers": "Kind and patient, always encouraging you to try your best.",
    "The Genie from Aladdin": "Magical and fun, making learning feel like an adventure.",
    "Dumbledore": "Wise and thoughtful, guiding you gently through challenges.",
    "Doraemon": "A futuristic cat robot who pulls out gadgets to solve any problem.",
    "Hermione Granger": "Brilliant, diligent, and always ready with the right book or spell.",
    "Sherlock Holmes": "Analytical and logical, teaching you how to think step by step.",
    "Yoda": "Wise mentor who guides with patience and cryptic but powerful lessons.",
    "Winnie the Pooh": "Gentle and kind, helping you approach challenges calmly and without stress.",
    "Baymax": "Caring, supportive, and always checking if you’re okay before tackling tough work.",
    "Tony Stark": "Tech genius who mixes humor with sharp problem-solving.",
    "Mulan": "Brave and determined, showing how persistence leads to mastery.",
    "Albert Einstein": "Playful scientist who makes complex ideas approachable.",
    "SpongeBob SquarePants": "Energetic, curious, and never afraid to ask 'why?' over and over."
}



def personalized_explanation(
    question= "",
    processed_response = {},
    lecturing_method = "Socratic/Questioning",
    characteristic = "Yoda",
    language = "Vietnamese",
    model: str = "gpt-4o"
) -> dict:
    """
    Generate a personalized explanation of the solution steps based on the user's level.
    Args:
        processed_response (dict): The processed response containing steps and answer.
        user_level (str): The user's level (e.g., "high school", "college").
        model (str): The model to use for generating the explanation.
    Returns:
        dict: A dictionary containing the personalized explanation.
    """
    steps = processed_response.get("steps", [])
    answer = processed_response.get("answer", "")
    if not steps or not answer:
        return processed_response
    # prompt = f"Explain the following solution steps of the following question in a {characteristic} manner using {lecturing_method} method. Make it easy to understand and engaging.\n\nQuestion: {question}\n\nSteps:\n" + "\n".join(steps) + f"\n\nFinal Answer: {answer}\n\nTeaching Method Description: {teaching_methods.get(lecturing_method, '')}\n\n"
    prompt = f"You are {characteristic}, a tutor who is {chacteristics_examples.get(characteristic, '')}. Explain the following solution steps of the following question in a {characteristic} manner using {lecturing_method} method. Make it easy to understand and engaging.\n\nQuestion: {question}\n\nSteps:\n" + "\n".join(steps) + f"\n\nFinal Answer: {answer}\n\nTeaching Method Description: {teaching_methods.get(lecturing_method, '')}\n\n"

    response_template = """## Solution:
<Solution with detailed explanation>
...

## Final Answer: <final answer (number or choice only, no sign or text, e.g., if answer is 42, just write 42, if answer is choice B, just write B)>
    """

    response_language = f"\n\nThe explanation should be in {language}.\n"
    response = generate(prompt + response_template + response_language + "Response:", model=model)
    return response

def image_parser(
    image_str: str,
    model: str = "gpt-4o"
) -> str:
    """
    Parse the image to extract question, choices and context in markdown format.
    Args:
        image_str (str): The base64 encoded string of the image.
        model (str): The model to use for parsing the image.
    Returns:
    str: The extracted question, choices and context in markdown format.
    """
    chat_ = [
        {"role": "system", "content": "You are a helpful assistant that can analyze images."},
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "Extract question, choices and context of the question in markdown from the image. Keep the language same as in the image. Say nothing else such as related fomula or answer."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_str}",
                    },
                },
            ],
        }
    ]
    response = client.chat.completions.create(
        model=model,
        messages=chat_,
        top_p=0.7,
    )
    return response.choices[0].message.content


def question_generator(
    sample_question = "",
    level = "high school",
    model: str = "gpt-4o",
    num_question: int = 3
):
    """
    Generate a new question similar to the sample question for the specified level.
    Args:
        sample_question (str): The sample question to base the new question on.
        level (str): The level of the students (e.g., "high school", "college").
        model (str): The model to use for generating the question.
    Returns:
        str: The generated question.
    """
    prompt = f"Generate {num_question} new question similar to the following question for {level} students. The new question should be different in context but similar in language, difficulty level and structure. Provide the questions in markdown format.\n\nSample Question:\n{sample_question}\n\nSay nothing else.\n\nResponse Template:"
    response_template = """## Question 1:
...
## Question 2: 
..."""
    response = generate(prompt + response_template + "New Questions:", model=model)

    print(response)
    return response