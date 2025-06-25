"""Validators for different file formats."""

from .base import (
    BaseValidator,
    ValidationResult,
    get_validator,
)

from .text_validator import (
    TextFileValidator,
    JsonFileValidator,
    CsvFileValidator,
    XmlFileValidator,
    YamlFileValidator,
    HtmlFileValidator,
    CssFileValidator,
    JavaScriptFileValidator,
    PythonFileValidator,
    ShellScriptValidator,
)

from .image_validator import (
    ImageValidator,
    JpegValidator,
    PngValidator,
    GifValidator,
    BmpValidator,
    WebPValidator,
    SvgValidator,
)

from .archive_validator import (
    ArchiveValidator,
    ZipValidator,
    TarValidator,
    TarGzValidator,
    TarBz2Validator,
    GzipValidator,
    Bzip2Validator,
)

from .pdf_validator import PdfValidator

from .office_validator import (
    OfficeValidator,
    DocxValidator,
    XlsxValidator,
    PptxValidator,
    OdtValidator,
    OdsValidator,
    OdpValidator,
    DocValidator,
    XlsValidator,
    PptValidator,
)

from .video_validator import (
    VideoValidator,
    Mp4Validator,
    AviValidator,
    MovValidator,
    MkvValidator,
    WebmValidator,
    # Add other video validators as needed
)

# Export all validators
__all__ = [
    # Base
    'BaseValidator',
    'ValidationResult',
    'get_validator',
    
    # Text
    'TextFileValidator',
    'JsonFileValidator',
    'CsvFileValidator',
    'XmlFileValidator',
    'YamlFileValidator',
    'HtmlFileValidator',
    'CssFileValidator',
    'JavaScriptFileValidator',
    'PythonFileValidator',
    'ShellScriptValidator',
    
    # Images
    'ImageValidator',
    'JpegValidator',
    'PngValidator',
    'GifValidator',
    'BmpValidator',
    'WebPValidator',
    'SvgValidator',
    
    # Archives
    'ArchiveValidator',
    'ZipValidator',
    'TarValidator',
    'TarGzValidator',
    'TarBz2Validator',
    'GzipValidator',
    'Bzip2Validator',
    
    # PDF
    'PdfValidator',
    
    # Office
    'OfficeValidator',
    'DocxValidator',
    'XlsxValidator',
    'PptxValidator',
    'OdtValidator',
    'OdsValidator',
    'OdpValidator',
    'DocValidator',
    'XlsValidator',
    'PptValidator',
    
    # Video
    'VideoValidator',
    'Mp4Validator',
    'AviValidator',
    'MovValidator',
    'MkvValidator',
    'WebmValidator',
    # Add other video validators to __all__ as needed
]
