from wordflux import DocxTranslator
from wordflux.utils.spinner import Spinner
import os
import sys
import argparse
import yaml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_config(config_path: str) -> dict:
    """Đọc config từ file YAML"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"✓ Loaded config from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"✗ Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"✗ Error parsing YAML config: {e}")
        raise

def main():
    config = load_config("config.yaml")
    parser = argparse.ArgumentParser(description="Translate a DOCX file")
    parser.add_argument("input_file", type=str, help="Input DOCX file")
    parser.add_argument("--output_dir", type=str, help="Output directory", default="output")
    args = parser.parse_args()

    input_file = args.input_file
    output_dir = args.output_dir
    openai_api_key = config.get("openai_api_key")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found in config. Please check your config.yaml file.")
    model = config.get("model")
    source_lang = config.get("source_lang")
    target_lang = config.get("target_lang")
    max_chunk_size = config.get("max_chunk_size")
    max_concurrent = config.get("max_concurrent")
    base_url = config.get("openai_api_base_url")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    print("⚙️ Starting DOCX translation process...\n")

    spinner = Spinner("Processing DOCX translation")
    spinner.start()
    try:
        docx_translator = DocxTranslator(input_file, output_dir, openai_api_key, model, source_lang, target_lang, max_chunk_size, max_concurrent, base_url)
        docx_translator.translate()
        spinner.stop()
        print(f"✅ Translation completed successfully!\n→ Output: {docx_translator.get_output_path()}")
    except Exception as e:
        spinner.stop()
        print(f"❌ Translation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()