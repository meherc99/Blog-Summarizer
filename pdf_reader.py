import io, unicodedata
from urllib.request import Request, urlopen

from PyPDF2 import PdfReader


def get_pdf_from_url(url):
    """
    Downloads a PDF file from a given URL and returns a PdfReader object.

    Args:
        url (str): The URL of the PDF file to download.

    Returns:
        PdfReader: A PdfReader object representing the downloaded PDF file.
    """

    remote_file = urlopen(Request(url)).read()
    memory_file = io.BytesIO(remote_file)
    pdf_file = PdfReader(memory_file)
    return pdf_file


def clean_data(page):
    """
    Cleans the text extracted from a PDF page by removing any unnecessary whitespace and normalizing the text.

    Args:
        page (pdfminer.high_level.Page): The PDF page to clean.

    Returns:
        str: The cleaned text from the PDF page.
    """
    page_text = page.extract_text()
    clean_text = unicodedata.normalize("NFKD", page_text).strip()

    return ''.join(clean_text.splitlines())


if __name__ == '__main__':
    dummy_url = 'https://iea.blob.core.windows.net/assets/830fe099-5530-48f2-a7c1-11f35d510983/WorldEnergyOutlook2022.pdf'

    raw_pdf = get_pdf_from_url(dummy_url)
    # clean_pdf = [clean_data(page) for page in raw_pdf.pages]

    print("Done")


'''
TODO :
1. Remove acknowledgements from pdf
2. Extract tables from pdf
3. Extract images from pdf
'''
