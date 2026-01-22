import json
import asyncio
import os
from wordflux.document.document import RunInfo, TextSegment, TableCellSegment, ChartSegment, SmartArtSegment
from wordflux.utils.decorator import timer, log_errors
from wordflux.utils.openai_client import OpenAIClientManager
from wordflux.utils.prompt_builder import PromptBuilder
import logging
import re
from collections import defaultdict
from tqdm import tqdm

logging.basicConfig(level=logging.WARNING)


class Translator:
    """Dịch nội dung từ checkpoint file sử dụng OpenAI API với async"""

    def __init__(self, checkpoint_file: str, openai_api_key: str, model: str = "gpt-4o-mini", source_lang: str = "English", target_lang: str = "Vietnamese", max_chunk_size: int = 5000, max_concurrent: int = 100, base_url: str = None):
        """
        Khởi tạo Translator

        Args:
            checkpoint_file: Đường dẫn đến checkpoint file
            config_path: Đường dẫn đến config file (mặc định: config.yaml)
        """
        self.checkpoint_file = checkpoint_file

        # Khởi tạo OpenAI client manager
        self.client_manager = OpenAIClientManager(openai_api_key=openai_api_key, base_url=base_url)
        self.client = self.client_manager.get_client()

        # Load config
        self.model = model
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.max_chunk_size = max_chunk_size
        self.max_concurrent = max_concurrent


        # Khởi tạo prompt builder
        self.prompt_builder = PromptBuilder(self.source_lang, self.target_lang)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

    async def _translate_text(self, text: str, context: str = "general") -> str:
        """Dịch một đoạn text sử dụng OpenAI API"""
        async with self.semaphore:
            try:
                messages = self.prompt_builder.build_messages(text)

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )

                return response.choices[0].message.content.strip()
            except Exception as e:
                self.logger.error(f"   ⚠️  Translation error: {e}")
                return text  # Trả về text gốc nếu có lỗi

    def _chunk_text_segments(self, text_segments: list[TextSegment]) -> list[list[TextSegment]]:
        """Ghép các text segments thành các chunks ~5000 ký tự"""
        chunks = []
        current_chunk = []
        current_size = 0

        for segment in text_segments:
            segment_size = len(segment['full_text'])

            # Nếu segment này làm vượt quá max_chunk_size, lưu chunk hiện tại và bắt đầu chunk mới
            if current_size + segment_size > self.max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_size = 0

            current_chunk.append(segment)
            current_size += segment_size

        # Thêm chunk cuối cùng
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _create_marked_text_from_runs(self, runs_list: list[RunInfo], prefix: str, idx: str) -> tuple[str, list[int]]:
        """Tạo text có đánh dấu từ danh sách runs - chỉ đánh dấu runs có nội dung

        Returns:
            tuple: (marked_text, translatable_indices) - text đã đánh dấu và danh sách indices cần dịch
        """
        marked_parts = []
        translatable_indices = []  # Lưu index của các runs cần dịch
        marker_idx = 0  # Counter cho markers (chỉ tăng cho runs thực sự cần dịch)

        for run_idx, run in enumerate(runs_list):
            text = run['text']

            # Kiểm tra xem run có nội dung cần dịch không (không chỉ là whitespace)
            if text.strip():
                # Run này cần dịch - tạo marker
                marked_parts.append(f"<R{marker_idx}>{text}</R{marker_idx}>")
                translatable_indices.append(run_idx)
                marker_idx += 1
            else:
                # Run này chỉ là whitespace - giữ nguyên không đánh dấu
                marked_parts.append(text)

        return "".join(marked_parts), translatable_indices

    def _extract_translated_runs(self, translated_text: str, runs_list: list[RunInfo], translatable_indices: list[int], prefix: str, idx: str) -> bool:
        """Trích xuất text đã dịch từ markers và gán vào runs

        Args:
            translated_text: Text đã dịch có chứa markers
            runs_list: Danh sách tất cả runs
            translatable_indices: Danh sách indices của runs đã được đánh dấu để dịch
            prefix: Prefix cho log
            idx: Index cho log
        """
        success = True

        # Dịch các runs có marker
        for marker_idx, run_idx in enumerate(translatable_indices):
            run = runs_list[run_idx]

            # Tìm text giữa markers: <R0>...</R0>
            pattern = f"<R{marker_idx}>(.*?)</R{marker_idx}>"
            match = re.search(pattern, translated_text, re.DOTALL)

            if match:
                translated_run_text = match.group(1)
                run['translated_text'] = translated_run_text
            else:
                # Nếu không tìm thấy marker, giữ nguyên text gốc
                self.logger.warning(f"   ⚠️  Marker <R{marker_idx}> not found in {prefix}-{idx}, keeping original text")
                run['translated_text'] = run['text']
                success = False

        # Các runs chỉ có whitespace giữ nguyên
        for run_idx, run in enumerate(runs_list):
            if run_idx not in translatable_indices:
                run['translated_text'] = run['text']

        return success

    async def _translate_text_chunk(self, chunk: list[TextSegment], progress_callback=None) -> list[TextSegment]:
        """Dịch một chunk các text segments với markers"""
        # Tạo text có đánh dấu cho từng segment
        marked_segments = []
        segment_translatable_map = {}  # Lưu translatable_indices cho mỗi segment

        for segment in chunk:
            seg_idx = segment['seg_idx']
            marked_text, translatable_indices = self._create_marked_text_from_runs(
                segment['runs_list'], 'seg', seg_idx
            )
            segment_translatable_map[seg_idx] = translatable_indices
            marked_segments.append(f"<SEG{seg_idx}>\n{marked_text}\n</SEG{seg_idx}>")

        combined_text = "\n\n".join(marked_segments)

        # Dịch toàn bộ chunk
        translated_combined = await self._translate_text(combined_text, context="document paragraphs")

        # Trích xuất kết quả dịch cho từng segment
        for segment in chunk:
            seg_idx = segment['seg_idx']

            # Tìm phần dịch của segment này
            seg_pattern = f"<SEG{seg_idx}>(.*?)</SEG{seg_idx}>"
            seg_match = re.search(seg_pattern, translated_combined, re.DOTALL)

            if seg_match:
                segment_translated = seg_match.group(1).strip()
                # Trích xuất từng run với translatable_indices
                translatable_indices = segment_translatable_map[seg_idx]
                self._extract_translated_runs(
                    segment_translated,
                    segment['runs_list'],
                    translatable_indices,
                    'seg',
                    seg_idx
                )

                # Cập nhật full_text từ translated_text
                segment['full_text'] = "".join(run.get('translated_text', run['text']) for run in segment['runs_list'])
            else:
                self.logger.warning(f"   ⚠️  Segment marker not found for seg-{seg_idx}, keeping original text")
                # Giữ nguyên text gốc
                for run in segment['runs_list']:
                    run['translated_text'] = run['text']

        # Update progress if callback provided
        if progress_callback:
            progress_callback()

        return chunk

    async def _translate_text_segments(self, text_segments: list[TextSegment], progress_callback=None):
        """Dịch tất cả text segments (theo chunks) với async"""
        chunks = self._chunk_text_segments(text_segments)
        self.logger.info(f"📦 Split {len(text_segments)} text segments into {len(chunks)} chunks")

        # Tạo tasks cho tất cả chunks
        tasks = [self._translate_text_chunk(chunk, progress_callback) for chunk in chunks]

        # Chạy tất cả tasks
        self.logger.info(f"🚀 Translating {len(chunks)} text chunks with max {self.max_concurrent} concurrent requests...")
        await asyncio.gather(*tasks)

    def _group_table_cells_by_table(self, table_cell_segments: list[TableCellSegment]) -> dict[int, list[TableCellSegment]]:
        """Nhóm các table cell segments theo table_idx"""
        grouped = defaultdict(list)
        for segment in table_cell_segments:
            grouped[segment['table_idx']].append(segment)
        return grouped

    async def _translate_table(self, table_idx: int, cells: list[TableCellSegment], progress_callback=None):
        """Dịch tất cả cells của một table trong một request"""
        # Tạo marked text cho tất cả cells
        marked_cells = []
        cell_translatable_map = {}

        for cell in cells:
            cell_id = f"{cell['table_idx']}-{cell['row_idx']}-{cell['cell_idx']}-{cell['para_idx']}"
            marked_text, translatable_indices = self._create_marked_text_from_runs(
                cell['runs_list'], 'cell', cell_id
            )
            cell_translatable_map[cell_id] = translatable_indices
            marked_cells.append(f"<CELL{cell_id}>\n{marked_text}\n</CELL{cell_id}>")

        combined_text = "\n\n".join(marked_cells)

        if combined_text.strip():
            # Dịch toàn bộ table
            translated_combined = await self._translate_text(combined_text, context=f"table {table_idx}")

            # Trích xuất kết quả cho từng cell
            for cell in cells:
                cell_id = f"{cell['table_idx']}-{cell['row_idx']}-{cell['cell_idx']}-{cell['para_idx']}"
                cell_pattern = f"<CELL{cell_id}>(.*?)</CELL{cell_id}>"
                cell_match = re.search(cell_pattern, translated_combined, re.DOTALL)

                if cell_match:
                    cell_translated = cell_match.group(1).strip()
                    translatable_indices = cell_translatable_map[cell_id]
                    self._extract_translated_runs(
                        cell_translated,
                        cell['runs_list'],
                        translatable_indices,
                        'cell',
                        cell_id
                    )
                else:
                    self.logger.warning(f"   ⚠️  Cell marker not found for {cell_id}, keeping original text")
                    for run in cell['runs_list']:
                        run['translated_text'] = run['text']

        # Update progress if callback provided
        if progress_callback:
            progress_callback()

    async def _translate_table_cell_segments(self, table_cell_segments: list[TableCellSegment], progress_callback=None):
        """Dịch tất cả table cell segments, nhóm theo table_idx"""
        grouped_tables = self._group_table_cells_by_table(table_cell_segments)
        self.logger.info(f"📊 Grouped {len(table_cell_segments)} cells into {len(grouped_tables)} tables")

        tasks = [self._translate_table(table_idx, cells, progress_callback) for table_idx, cells in grouped_tables.items()]

        self.logger.info(f"🚀 Translating {len(tasks)} tables with max {self.max_concurrent} concurrent requests...")
        await asyncio.gather(*tasks)

    def _group_charts_by_idx(self, chart_segments: list[ChartSegment]) -> dict[int, list[ChartSegment]]:
        """Nhóm các chart segments theo chart_idx"""
        grouped = defaultdict(list)
        for segment in chart_segments:
            grouped[segment['chart_idx']].append(segment)
        return grouped

    async def _translate_chart(self, chart_idx: int, elements: list[ChartSegment], progress_callback=None):
        """Dịch tất cả elements của một chart trong một request"""
        marked_elements = []
        for elem in elements:
            elem_id = f"{chart_idx}-{elem['element_type']}-{elem['element_idx']}"
            if elem['text'].strip():
                marked_elements.append(f"<CHART{elem_id}>{elem['text']}</CHART{elem_id}>")

        combined_text = "\n\n".join(marked_elements)

        if combined_text.strip():
            # Dịch toàn bộ chart
            translated_combined = await self._translate_text(combined_text, context=f"chart {chart_idx}")

            # Trích xuất kết quả cho từng element
            for elem in elements:
                elem_id = f"{chart_idx}-{elem['element_type']}-{elem['element_idx']}"
                pattern = f"<CHART{elem_id}>(.*?)</CHART{elem_id}>"
                match = re.search(pattern, translated_combined, re.DOTALL)

                if match:
                    elem['translated_text'] = match.group(1)
                else:
                    if elem['text'].strip():
                        self.logger.warning(f"   ⚠️  Marker not found for chart-{elem_id}, keeping original text")
                    elem['translated_text'] = elem['text']

        # Update progress if callback provided
        if progress_callback:
            progress_callback()

    async def _translate_chart_segments(self, chart_segments: list[ChartSegment], progress_callback=None):
        """Dịch tất cả chart segments, nhóm theo chart_idx"""
        grouped_charts = self._group_charts_by_idx(chart_segments)
        self.logger.info(f"📈 Grouped {len(chart_segments)} elements into {len(grouped_charts)} charts")

        tasks = [self._translate_chart(chart_idx, elements, progress_callback) for chart_idx, elements in grouped_charts.items()]

        self.logger.info(f"🚀 Translating {len(tasks)} charts with max {self.max_concurrent} concurrent requests...")
        await asyncio.gather(*tasks)

    def _group_smartarts_by_idx(self, smartart_segments: list[SmartArtSegment]) -> dict[int, list[SmartArtSegment]]:
        """Nhóm các smartart segments theo smartart_idx"""
        grouped = defaultdict(list)
        for segment in smartart_segments:
            grouped[segment['smartart_idx']].append(segment)
        return grouped

    async def _translate_smartart(self, smartart_idx: int, elements: list[SmartArtSegment], progress_callback=None):
        """Dịch tất cả elements của một SmartArt trong một request"""
        marked_elements = []
        for elem in elements:
            elem_id = f"{smartart_idx}-{elem['element_idx']}"
            if elem['text'].strip():
                marked_elements.append(f"<SMART{elem_id}>{elem['text']}</SMART{elem_id}>")

        combined_text = "\n\n".join(marked_elements)

        if combined_text.strip():
            # Dịch toàn bộ SmartArt
            translated_combined = await self._translate_text(combined_text, context=f"SmartArt {smartart_idx}")

            # Trích xuất kết quả cho từng element
            for elem in elements:
                elem_id = f"{smartart_idx}-{elem['element_idx']}"
                pattern = f"<SMART{elem_id}>(.*?)</SMART{elem_id}>"
                match = re.search(pattern, translated_combined, re.DOTALL)

                if match:
                    elem['translated_text'] = match.group(1)
                else:
                    if elem['text'].strip():
                        self.logger.warning(f"   ⚠️  Marker not found for smart-{elem_id}, keeping original text")
                    elem['translated_text'] = elem['text']

        # Update progress if callback provided
        if progress_callback:
            progress_callback()

    async def _translate_smartart_segments(self, smartart_segments: list[SmartArtSegment], progress_callback=None):
        """Dịch tất cả SmartArt segments, nhóm theo smartart_idx"""
        grouped_smartarts = self._group_smartarts_by_idx(smartart_segments)
        self.logger.info(f"🎨 Grouped {len(smartart_segments)} elements into {len(grouped_smartarts)} SmartArts")

        tasks = [self._translate_smartart(smartart_idx, elements, progress_callback) for smartart_idx, elements in grouped_smartarts.items()]

        self.logger.info(f"🚀 Translating {len(tasks)} SmartArts with max {self.max_concurrent} concurrent requests...")
        await asyncio.gather(*tasks)

    async def _translate_all(self):
        """Hàm async chính để dịch tất cả - CHẠY SONG SONG"""
        # Đọc checkpoint
        with open(self.checkpoint_file, "r", encoding="utf-8") as f:
            checkpoint_data = json.load(f)

        total_tasks = 0
        text_segments = checkpoint_data.get("text_segments", [])
        table_cell_segments = checkpoint_data.get("table_cell_segments", [])
        chart_segments = checkpoint_data.get("chart_segments", [])
        smartart_segments = checkpoint_data.get("smartart_segments", [])

        if text_segments:
            total_tasks += len(self._chunk_text_segments(text_segments))

        if table_cell_segments:
            total_tasks += len(self._group_table_cells_by_table(table_cell_segments))

        if chart_segments:
            total_tasks += len(self._group_charts_by_idx(chart_segments))

        if smartart_segments:
            total_tasks += len(self._group_smartarts_by_idx(smartart_segments))

        if total_tasks == 0:
            self.logger.info("No content to translate.")
            return

        with tqdm(total=total_tasks, desc="Translating content", unit="task") as pbar:
            progress_callback = pbar.update
            all_tasks = []

            if text_segments:
                all_tasks.append(self._translate_text_segments(text_segments, progress_callback))

            if table_cell_segments:
                all_tasks.append(self._translate_table_cell_segments(table_cell_segments, progress_callback))

            if chart_segments:
                all_tasks.append(self._translate_chart_segments(chart_segments, progress_callback))

            if smartart_segments:
                all_tasks.append(self._translate_smartart_segments(smartart_segments, progress_callback))

            # CHẠY TẤT CẢ SONG SONG
            if all_tasks:
                self.logger.info(f"🔥 Starting parallel translation for {total_tasks} tasks...")
                await asyncio.gather(*all_tasks)

        # Lưu lại checkpoint đã dịch
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"✅ Translation completed and saved to {self.checkpoint_file}")
        self.logger.info(f"Total translated:")
        self.logger.info(f"  - Text segments: {len(checkpoint_data['text_segments'])}")
        self.logger.info(f"  - Table cell segments: {len(checkpoint_data['table_cell_segments'])}")
        self.logger.info(f"  - Chart segments: {len(checkpoint_data['chart_segments'])}")
        self.logger.info(f"  - SmartArt segments: {len(checkpoint_data['smartart_segments'])}")

    @timer
    @log_errors
    def translate(self, progress_callback=None):
        """Đọc checkpoint, dịch tất cả nội dung và lưu lại"""
        self.logger.info("="*70)
        self.logger.info("TRANSLATING ALL CONTENT WITH PARALLEL ASYNC AND MARKERS")
        self.logger.info("="*70 + "\n")

        # Chạy async function
        asyncio.run(self._translate_all())