import modal
import os

from modal import FilePatternMatcher

app = modal.App("STEMMate")

# Define image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements("requirements.txt")
    .apt_install("rsync")  # Use Modal's built-in method for apt installs
)

# Add source code to image (exclude virtual envs)
image = image.add_local_dir(
    ".",
    "/app",
    copy=True,
    ignore=FilePatternMatcher("**/venv/**", "**/.venv/**", "**/__pycache__/**")
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-secrets")],
    timeout=600,
    max_containers=1,
    memory=8192,
)
@modal.asgi_app()
def gradio_app():
    import sys
    sys.path.append("/app")
    
    # Check environment variables
    print(f"API Key loaded: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
    print(f"Base URL: {os.getenv('OPENAI_API_BASE_URL', 'Not set')}")
    
    # Import and setup Gradio app
    from main import demo
    from fastapi import FastAPI
    
    app = FastAPI()
    demo.queue(max_size=20)
    
    # Mount Gradio app
    from gradio.routes import mount_gradio_app
    return mount_gradio_app(app=app, blocks=demo, path="/")