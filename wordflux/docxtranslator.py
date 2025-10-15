import os
from wordflux.worker.extractor import Extractor
from wordflux.worker.injector import Injector
from wordflux.worker.translator import Translator


class DocxTranslator:
    """
    Translate a DOCX file while preserving formatting
    Author: Pham Nguyen Ngoc Bao
    Email: pnnbao@gmail.com
    GitHub: https://github.com/pnnbao97
    Facebook: https://www.facebook.com/pnnbao
    """

    def __init__(self, input_file: str, output_dir: str = "output", openai_api_key: str = "", model: str = "gpt-4o-mini", source_lang: str = "English", target_lang: str = "Vietnamese", max_chunk_size: int = 5000, max_concurrent: int = 100):
        self.input_file = input_file
        self.output_dir = output_dir
        self.openai_api_key = openai_api_key
        self.model = model
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.max_chunk_size = max_chunk_size
        self.max_concurrent = max_concurrent
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please provide a valid OpenAI API key.")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Derive filenames
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        self.checkpoint_file = os.path.join(output_dir, f"{file_name}_checkpoint.json")
        self.output_file = os.path.join(output_dir, f"{file_name}_translated.docx")

        # Initialize pipeline components
        self.extractor = Extractor(self.input_file, self.checkpoint_file)
        self.translator = Translator(self.checkpoint_file, self.openai_api_key, self.model, self.source_lang, self.target_lang, self.max_chunk_size, self.max_concurrent)
        self.injector = Injector(self.input_file, self.checkpoint_file, self.output_file)

    def translate(self):
        """Run the entire translation pipeline"""
        self.extract()
        self.translator.translate()
        self.inject()

    def extract(self):
        """Extract segments and save checkpoint"""
        self.extractor.extract()

    def inject(self):
        """Inject translated segments into a new DOCX file"""
        self.injector.inject()

    def get_output_path(self) -> str:
        """Return the absolute path of the translated file"""
        return os.path.abspath(self.output_file)