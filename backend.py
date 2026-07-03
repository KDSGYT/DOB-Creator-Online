from pypdf import PdfWriter, PdfReader
from io import BytesIO
import datetime as dt


def get_date():
    """Return the package date parts.

    After 7 PM the package is prepared for the next day.
    """
    hour = int(dt.datetime.now().strftime("%H"))
    if 19 <= hour < 24:
        date = dt.date.today() + dt.timedelta(days=1)
    else:
        date = dt.date.today()

    month = date.strftime("%B")
    day = f"{date.day:02d}"
    year = date.year

    return month, day, year


# Create file names for DOB packages
def create_file_names():
    month, day, year = get_date()

    dob_print_output_file = f"Complete DOB Package (print version) {month} {day}, {year}.pdf"
    dob_email_output_file = f"Complete DOB Package {month} {day}, {year}.pdf"
    don_output_file = f"DON Package {month} {day}, {year}.pdf"
    cp_output_file = f"CP DOB {month} {day}, {year}.pdf"
    metro_output_file = f"Metrolinx DOB {month} {day}, {year}.pdf"

    return (
        dob_print_output_file,
        dob_email_output_file,
        don_output_file,
        cp_output_file,
        metro_output_file,
    )


def _reader_source(file):
    """Return a fresh PDF source for paths, uploaded files, bytes, or streams."""
    if isinstance(file, bytes):
        return BytesIO(file)
    if isinstance(file, tuple):
        if len(file) == 3:
            source_type, _name, payload = file
            if source_type == "upload":
                return BytesIO(payload)
            if source_type == "path":
                return payload
        return file

    getvalue = getattr(file, "getvalue", None)
    if callable(getvalue):
        data = getvalue()
        return BytesIO(data)  # type: ignore[arg-type]
    return file


def combine(list_of_pdfs):
    """Combine PDFs and insert a blank page after odd-page documents."""
    merger = PdfWriter()

    for file in list_of_pdfs:
        source = _reader_source(file)
        reader = PdfReader(source)
        number_of_pages = len(reader.pages)

        merger.append(reader)
        if number_of_pages % 2 != 0:
            merger.append("./PDFs/blank.pdf")

    byte_stream = BytesIO()
    merger.write(byte_stream)
    merger.close()
    byte_stream.seek(0)
    return byte_stream
