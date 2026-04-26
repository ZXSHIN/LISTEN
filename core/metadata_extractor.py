"""File Metadata Extractor - EXIF, PDF, DOCX"""

import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def extract_metadata(filepath: str) -> dict:
    result = {"file": filepath, "error": None, "metadata": {}}
    if not os.path.exists(filepath):
        result["error"] = "File not found"
        return result

    ext = os.path.splitext(filepath)[1].lower()
    result["metadata"]["File Size"] = _format_size(os.path.getsize(filepath))
    result["metadata"]["Extension"] = ext

    if ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp"]:
        _extract_image(filepath, result)
    elif ext == ".pdf":
        _extract_pdf(filepath, result)
    elif ext in [".docx", ".doc"]:
        _extract_docx(filepath, result)
    else:
        result["error"] = f"Unsupported file type: {ext}"

    return result


def _extract_image(filepath, result):
    try:
        img = Image.open(filepath)
        result["metadata"]["Format"] = img.format or "Unknown"
        result["metadata"]["Mode"] = img.mode
        result["metadata"]["Size (px)"] = f"{img.width} x {img.height}"

        exif_data = img._getexif()
        if exif_data:
            gps_info = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    for gps_id, gps_val in value.items():
                        gps_tag = GPSTAGS.get(gps_id, gps_id)
                        gps_info[gps_tag] = gps_val
                else:
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='replace')
                        except Exception:
                            value = str(value)
                    result["metadata"][str(tag)] = str(value)

            if gps_info:
                lat = _convert_gps(gps_info.get("GPSLatitude"), gps_info.get("GPSLatitudeRef"))
                lon = _convert_gps(gps_info.get("GPSLongitude"), gps_info.get("GPSLongitudeRef"))
                if lat and lon:
                    result["metadata"]["GPS Latitude"] = f"{lat:.6f}"
                    result["metadata"]["GPS Longitude"] = f"{lon:.6f}"
                    result["metadata"]["Google Maps"] = (
                        f"https://maps.google.com/?q={lat},{lon}"
                    )
        else:
            result["metadata"]["EXIF"] = "No EXIF data found"
    except Exception as e:
        result["error"] = str(e)


def _convert_gps(value, ref):
    if not value or not ref:
        return None
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        decimal = d + m / 60 + s / 3600
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return None


def _extract_pdf(filepath, result):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        meta = doc.metadata
        result["metadata"]["Pages"] = str(doc.page_count)
        for k, v in meta.items():
            if v:
                result["metadata"][k.capitalize()] = v
        doc.close()
    except ImportError:
        result["metadata"]["Note"] = "PyMuPDF not installed (pip install PyMuPDF)"
    except Exception as e:
        result["error"] = str(e)


def _extract_docx(filepath, result):
    try:
        from docx import Document
        doc = Document(filepath)
        props = doc.core_properties
        fields = {
            "Author": props.author,
            "Title": props.title,
            "Subject": props.subject,
            "Created": str(props.created),
            "Modified": str(props.modified),
            "Last Modified By": props.last_modified_by,
            "Revision": str(props.revision),
            "Keywords": props.keywords,
            "Description": props.description,
        }
        for k, v in fields.items():
            if v and v != "None":
                result["metadata"][k] = v
    except ImportError:
        result["metadata"]["Note"] = "python-docx not installed (pip install python-docx)"
    except Exception as e:
        result["error"] = str(e)


def _format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
