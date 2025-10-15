# WordFlux 🌀

> **Translate DOCX using OpenAI - Preserve Format**

WordFlux is a powerful and intelligent tool for translating Microsoft Word documents (.docx) using OpenAI API while preserving the original formatting, structure, and layout completely.

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

# Initialize with API key directly
translator = DocxTranslator(
    input_file="document.docx",
    output_dir="output",
    openai_api_key="sk-your-openai-api-key-here",  # Your API key here
    model="gpt-4o-mini",
    source_lang="English",
    target_lang="Vietnamese"
)
```

### Advanced Usage with Custom Settings

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

### Async Usage

```python
import asyncio
from wordflux import DocxTranslator

async def translate_document():
    # Initialize translator
    translator = DocxTranslator(
        input_file="document.docx",
        output_dir="output",
        openai_api_key="sk-your-openai-api-key-here",
        source_lang="English",
        target_lang="Vietnamese"
    )
    
    # Use async translation method
    await translator.atranslate()
    
    print(f"Async translation completed: {translator.get_output_path()}")

# Run async function
asyncio.run(translate_document())
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
- `gpt-4o-mini` (default, cost-effective)
- `gpt-4o`
- `gpt-4`
- `gpt-3.5-turbo`
- And other OpenAI models

## 📖 Usage

### 1. Command Line Usage

```bash
# Translate DOCX file
python main.py input_file.docx

# Specify output directory
python main.py input_file.docx --output_dir ./my_output

# Concrete example
python main.py document.docx --output_dir ./translated_docs
```

### 2. Use as Python Module

```python
from wordflux import DocxTranslator

# Initialize translator
translator = DocxTranslator(
    input_file="document.docx",
    output_dir="output",
    openai_api_key="your-api-key",
    model="gpt-4o-mini",
    source_lang="English",
    target_lang="Vietnamese",
    max_chunk_size=5000,
    max_concurrent=100
)

# Perform translation
translator.translate()

# Get translated file path
output_path = translator.get_output_path()
print(f"Translated file: {output_path}")
```

### 3. Step-by-step Usage

```python
from wordflux import DocxTranslator

translator = DocxTranslator("document.docx", "output", "your-api-key")

# Step 1: Extract content
translator.extract()

# Step 2: Translate content
translator.translator.translate()

# Step 3: Inject translations into file
translator.inject()
```

## 🔧 Advanced Configuration

### Performance Tuning

```yaml
# config.yaml
max_concurrent: 50      # Reduce if encountering rate limit errors
max_chunk_size: 3000    # Reduce for complex documents
```

### Change Languages

```yaml
source_lang: "English"
target_lang: "French"   # Or "Spanish", "German", "Chinese", etc.
```

### Use Different Models

```yaml
model: "gpt-5"         # More powerful model, more expensive

```

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

## 🎯 Usage Examples

### Simple Document Translation

```bash
# Translate document.docx from English to Vietnamese
python main.py document.docx
```


## 🚨 Error Handling

### API Key Error
```
❌ Translation failed: OpenAI API key not found in config
```
**Solution:** Check `config.yaml` file and ensure API key is correct.

### Rate Limit Error
```
❌ Translation failed: Rate limit exceeded
```
**Solution:** Reduce `max_concurrent` in `config.yaml` from 100 to 50 or 25.

### File Not Found Error
```
❌ Translation failed: [Errno 2] No such file or directory: 'document.docx'
```
**Solution:** Check input file path.

## 💡 Tips and Tricks

### 1. **Cost Optimization**
- Use `gpt-4o-mini` instead of `gpt-4o` for simple documents
- Adjust `max_chunk_size` according to content

### 2. **Speed Optimization**
- Increase `max_concurrent` if you have high API quota
- Use SSD for temporary file storage

### 3. **Large Document Handling**
- Split large documents into smaller files
- Use checkpoint system to resume if interrupted

### 4. **Quality Control**
- Always review translations before use
- Adjust prompts if necessary

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

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

## 📞 Support

If you encounter issues or have questions:

1. 📖 Read this documentation carefully
2. 🔍 Check [Issues](https://github.com/pnnbao97/wordflux/issues)
3. 🆕 Create a new issue if no solution exists
4. 📧 Contact directly: pnnbao@gmail.com

---

**WordFlux** - Smart document translation with perfect formatting preservation! 🌀✨