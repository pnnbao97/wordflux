class PromptBuilder:
    """Xây dựng prompts cho OpenAI API"""
    
    def __init__(self, source_lang: str, target_lang: str):
        """Khởi tạo PromptBuilder"""
        self.source_lang = source_lang
        self.target_lang = target_lang
    
    def build_system_prompt(self) -> str:
        """Xây dựng system prompt cho translation"""
        return (
            f"You are a professional translator from {self.source_lang} to {self.target_lang}.\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. The text contains XML-like markers (e.g., <R0>, <R1>, <R2>).\n"
            f"2. These markers are STRUCTURAL TAGS that MUST be preserved EXACTLY.\n"
            f"3. PRESERVE ALL WHITESPACE (spaces, newlines) at the START and END of text inside markers.\n\n"
            f"YOUR TASK:\n"
            f"- Keep ALL markers with exact numbers: <R0>, <R1>, <R2>, etc.\n"
            f"- Keep ALL closing tags: </R0>, </R1>, </R2>, etc.\n"
            f"- ONLY translate the text BETWEEN markers\n"
            f"- PRESERVE leading/trailing spaces inside each marker\n"
            f"- Do NOT merge, skip, or renumber any markers\n"
            f"- Output must have the SAME NUMBER of markers as input\n\n"
            f"WHITESPACE EXAMPLES:\n"
            f"Input:  <R0>Hello </R0><R1>world</R1>\n"
            f"Output: <R0>Xin chào </R0><R1>thế giới</R1>\n"
            f"(Note: Space after 'Hello' is preserved after 'Xin chào')\n\n"
            f"Input:  <R0>Start</R0><R1> middle </R1><R2>end</R2>\n"
            f"Output: <R0>Bắt đầu</R0><R1> giữa </R1><R2>kết thúc</R2>\n"
            f"(Note: Spaces before and after 'middle' are preserved)"
        )
    
    def build_user_prompt(self, text: str) -> str:
        """Xây dựng user prompt"""
        return text
    
    def build_messages(self, text: str) -> list[dict]:
        """Xây dựng messages array cho OpenAI API"""
        return [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": self.build_user_prompt(text)}
        ]