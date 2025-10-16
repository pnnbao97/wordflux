# WordFlux 🌀

> **Translate DOCX using OpenAI - Preserve Format**

WordFlux is a powerful and intelligent tool for translating Microsoft Word documents (.docx) using OpenAI API while preserving the original formatting, structure, and layout completely.
<img width="1565" height="997" alt="image" src="https://github.com/user-attachments/assets/dc2ae795-75c4-4a63-a4ef-2fa29d12dcfb" />




## 🚀 Installation

### System Requirements
- Python 3.12+
- OpenAI API key

### Install from pip

```bash
pip install wordflux
```

## 🔑 API Key Setup

After installation, you need to set up your OpenAI API key. 

```python
from wordflux import DocxTranslator

# Advanced configuration
translator = DocxTranslator(
    input_file="complex_document.docx",
    output_dir="./translated_docs",
    openai_api_key="sk-your-openai-api-key-here",
    model="gpt-5",                    # Use more powerful model
    source_lang="English",
    target_lang="French",
    max_chunk_size=3000,              # Smaller chunks for complex docs
    max_concurrent=50                 # Fewer concurrent requests
)

# Step-by-step processing
translator.translate()

print("Translation completed!")
```


### Install from source

```bash
# Clone repository
git clone https://github.com/pnnbao97/wordflux.git
cd wordflux

# Install dependencies
pip install -e .
```

### Manual dependency installation

```bash
pip install openai>=2.3.0 python-docx>=1.2.0 pyyaml>=6.0.3 tqdm>=4.67.1
```

## ⚙️ Configuration

Create a `config.yaml` file in the root directory:

```yaml
# OpenAI Configuration
openai_api_key: "sk-your-openai-api-key-here"  # Replace with your API key
model: "gpt-4o-mini"  # Can use gpt-4, gpt-3.5-turbo, etc.

# Translation Settings
source_lang: "English"
target_lang: "Vietnamese"

# Performance Settings
max_concurrent: 100      # Maximum concurrent requests
max_chunk_size: 5000     # Maximum chunk size (characters)
```

### Supported OpenAI Models
- `gpt-5-mini`
- `gpt-5`
- `gpt-5-pro`
- `gpt-5-nano`
- And other OpenAI models

## 📁 Project Structure

```
wordflux/
├── 📄 main.py                 # Entry point
├── ⚙️ config.yaml            # Configuration
├── 📋 pyproject.toml         # Project metadata
├── 📖 README.md              # This documentation
├── 🗂️ output/               # Output directory for translated files
│   ├── document_translated.docx
│   └── document_checkpoint.json
└── 📦 wordflux/              # Main package
    ├── 📄 __init__.py
    ├── 🔧 docxtranslator.py  # Main class
    ├── 📄 document/          # Data models
    │   └── document.py
    ├── 🔨 worker/            # Core workers
    │   ├── extractor.py      # Extract content
    │   ├── translator.py     # Translate content
    │   └── injector.py       # Inject translations
    └── 🛠️ utils/             # Utilities
        ├── decorator.py      # Decorators (timer, retry, etc.)
        ├── is_numeric.py     # Helper functions
        ├── openai_client.py  # OpenAI client manager
        ├── prompt_builder.py # Build prompts
        └── spinner.py        # Loading spinner
```

## 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

## 👨‍💻 Author

**Pham Nguyen Ngoc Bao**
- 📧 Email: pnnbao@gmail.com
- 🐙 GitHub: [@pnnbao97](https://github.com/pnnbao97)
- 📘 Facebook: [pnnbao](https://www.facebook.com/pnnbao)

## 🙏 Acknowledgments

- OpenAI API for powerful translation capabilities
- python-docx library for DOCX file processing
- Python community for supporting libraries

---

**WordFlux** - Smart document translation with perfect formatting preservation! 🌀✨
