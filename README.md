# 🧮 STEMMate

STEMMate is an AI-powered application designed to solve math problems from images and provide step-by-step solutions with personalized explanations. It leverages multiple AI models to ensure accuracy and offers customizable teaching styles and tutor characteristics.

## 🚀 Features

- **Image-Based Math Problem Solving**: Upload an image containing a math question, and STEMMate will extract and solve it.
- **Step-by-Step Solutions**: Get detailed steps for solving the problem.
- **Personalized Explanations**: Choose from various teaching methods and tutor characteristics for tailored explanations.
- **Multi-Model Consensus**: Enable multiple AI models for better accuracy.
- **Customizable Settings**: Configure models, teaching styles, and tutor characteristics to suit your needs.

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd STEMMate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a 

.env

 file in the root directory.
   - Add the following variables:
     ```
     OPENAI_API_KEY=<your_openai_api_key>
     OPENAI_API_BASE_URL=<your_openai_api_base_url>
     ```

4. Run the application:
   ```bash
   python main.py
   ```

## 🖼️ Usage

1. Launch the application by running the command above.
2. Open the web interface in your browser (default: `http://0.0.0.0:7860`).
3. Upload an image containing a math question.
4. Configure settings such as:
   - **Multi-Model Consensus**: Enable or disable multiple models.
   - **Explanation Style**: Choose from teaching methods like "Lecture/Direct Instruction" or "Socratic/Questioning."
   - **Tutor Characteristic**: Select a tutor persona like "Yoda" or "Albert Einstein."
5. Click the **Solve Question** button to get results.

## 📋 Output Tabs

- **Summary**: Extracted question and final answer.
- **Detailed Steps**: Step-by-step solution provided by the models.
- **Explanation**: Personalized explanation based on your selected settings.
- **Model Comparison**: Confidence levels and answers from different models.

## 💡 Tips

- Upload clear images with readable text for better results.
- Enable multi-model consensus for improved accuracy.
- Use the settings to customize the solving process and explanations.

## 🧰 Development

### Running with Modal
This project uses [Modal](https://modal.com) for deployment. To run the app with Modal:
1. Ensure you have the Modal CLI installed and authenticated.
2. Run the following command:
   ```bash
   modal run modal_app.py
   ```


## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

