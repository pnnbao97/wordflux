from dataclasses import dataclass, field

@dataclass
class RunInfo:
    """Thông tin định dạng của một đoạn văn bản"""
    text: str
    bold: bool | None
    italic: bool | None
    underline: bool | None
    superscript: bool | None
    subscript: bool | None
    translated_text: str = ""

    def __eq__(self, other):
        return (
            self.bold == other.bold
            and self.italic == other.italic
            and self.underline == other.underline
            and self.superscript == other.superscript
            and self.subscript == other.subscript
        )

@dataclass
class TextSegment:
    """Đoạn văn bản thông thường trong tài liệu"""
    seg_idx: int
    full_text: str
    has_smartart_or_chart: bool = False
    runs_list: list[RunInfo] = field(default_factory=list)

@dataclass
class TableCellSegment:
    """Đoạn văn bản trong ô bảng"""
    table_idx: int
    row_idx: int
    cell_idx: int
    para_idx: int
    runs_list: list[RunInfo] = field(default_factory=list)

@dataclass
class ChartSegment:
    """Đoạn văn bản trong biểu đồ"""
    chart_idx: int
    element_type: str  # "title", "value", "category"
    element_idx: int
    text: str
    file_path: str
    translated_text: str = ""

@dataclass
class SmartArtSegment:
    """Đoạn văn bản trong SmartArt"""
    smartart_idx: int
    element_idx: int
    text: str
    file_path: str
    translated_text: str = ""