import backend
import streamlit as st


st.set_page_config(
    page_title="Alstom-DCOT",
    layout="wide",
)

st.header('Alstom-DCOT')


# Slots that appear in the complete DOB package, in package order.
# source="upload" means the user uploads the PDF each time.
# source="builtin" means the app uses a PDF already stored in the PDFs folder.
DOB_SLOTS = [
    {
        'key': 'greater_metro',
        'title': 'Greater METRO',
        'source': 'upload',
    },
    {
        'key': 'mx_bala',
        'title': 'MX BALA',
        'source': 'upload',
    },
    {
        'key': 'mx_newmarket_pearson_weston',
        'title': 'MX NewMarket, PEARSON, WESTON',
        'source': 'upload',
    },
    {
        'key': 'mx_guelph',
        'title': 'MX Guelph',
        'source': 'upload',
    },
    {
        'key': 'cp_toronto_west',
        'title': 'CP Toronto West',
        'source': 'upload',
    },
    {
        'key': 'cp_hamilton',
        'title': 'CP Hamilton',
        'source': 'upload',
    },
    {
        'key': 'crew_predeparture_checklist',
        'title': 'Crew Pre-departure Checklist',
        'source': 'builtin',
        'path': './PDFs/Predeparture Checklist Template  - 2025-12-22.pdf',
    },
    {
        'key': 'en_route_job_briefings',
        'title': 'En-Route job briefings',
        'source': 'builtin',
        'path': './PDFs/En route job briefings - Rev Apr 16, 2026.pdf',
    },
    {
        'key': 'reversing_respotting_checklist',
        'title': 'Reversing/Re-Spotting Checklist',
        'source': 'builtin',
        'path': './PDFs/Reversing Re-Spotting Checklist updated April 02 2026.pdf',
    },
    {
        'key': 'mx_don',
        'title': 'MX DON',
        'source': 'upload',
    },
    {
        'key': 'ehs_form',
        'title': 'EHS Form',
        'source': 'builtin',
        'path': './PDFs/EHS Concern  Form updated PDF 10.04.2026.pdf',
    },
    {
        'key': 'station_to_station_notepad',
        'title': 'Station to Station Notepad',
        'source': 'builtin',
        'path': './PDFs/Station to Station Notepad.pdf',
    },
    {
        'key': 'radio_channel_guide',
        'title': 'Radio Channel Guide',
        'source': 'builtin',
        'path': './PDFs/Radio Channel Guide July 23rd.pdf',
    },
    {
        'key': 'stratford_tgobs',
        'title': 'STRATFORD TGOBs',
        'source': 'upload',
    },
    {
        'key': 'goderich_exeter_railway',
        'title': 'Goderich & Exeter Railway',
        'source': 'upload',
    },
]


# These keys are used for the extra package download buttons.
SLOT_BY_KEY = {slot['key']: slot for slot in DOB_SLOTS}


def pdf_uploader(column, title, helper_text, key_prefix):
    reset_key = f'{key_prefix}_reset'
    if reset_key not in st.session_state:
        st.session_state[reset_key] = 0

    column.subheader(title)
    if helper_text:
        column.write(helper_text)

    uploaded_file = column.file_uploader(
        'PDF upload',
        type=['pdf'],
        key=f'{key_prefix}_{st.session_state[reset_key]}',
        label_visibility='collapsed',
    )
    if uploaded_file is not None:
        if column.form_submit_button('Remove file', key=f'remove_{key_prefix}'):
            st.session_state[reset_key] += 1
            st.rerun()

    return uploaded_file


def render_uploader_grid(upload_slots, columns_per_row=3):
    uploaded_files = {}
    for start in range(0, len(upload_slots), columns_per_row):
        columns = st.columns(columns_per_row)
        for column, slot in zip(columns, upload_slots[start:start + columns_per_row]):
            uploaded_files[slot['key']] = pdf_uploader(
                column,
                slot['title'],
                'Upload PDF for this DOB slot.',
                slot['key'],
            )
    return uploaded_files


def get_slot_file(slot, uploaded_files):
    if slot['source'] == 'builtin':
        return slot['path']
    return uploaded_files.get(slot['key'])


with st.form("my_form"):
    st.subheader('Cover Pages')
    cover_col1, cover_col2 = st.columns(2)
    dob_cover_page = pdf_uploader(
        cover_col1,
        'DOB Cover Page',
        'Leave blank to use default cover page.',
        'dob_cover_page',
    )
    don_cover_page = pdf_uploader(
        cover_col2,
        'DON Cover Page',
        'Leave blank to use default cover page.',
        'don_cover_page',
    )

    st.divider()
    st.subheader('DOB Upload Slots')
    upload_slots = [slot for slot in DOB_SLOTS if slot['source'] == 'upload']
    uploaded_files = render_uploader_grid(upload_slots)

    st.divider()
    st.form_submit_button('Create Packages')


if dob_cover_page is None:
    dob_cover_page = './PDFs/Permanent DOB  DON Coverpage.pdf'
if don_cover_page is None:
    don_cover_page = './PDFs/Permanent DOB  DON Coverpage.pdf'

slot_files = {
    slot['key']: get_slot_file(slot, uploaded_files)
    for slot in DOB_SLOTS
}

DOB_to_email_files = [slot_files[slot['key']] for slot in DOB_SLOTS]
DOB_to_print_files = [dob_cover_page] + DOB_to_email_files

don_package_files = [
    don_cover_page,
    slot_files['mx_don'],
    slot_files['ehs_form'],
    slot_files['radio_channel_guide'],
]
cp_package_files = [
    slot_files['cp_toronto_west'],
    slot_files['cp_hamilton'],
]

# get desktop location and filenames
dob_print_output_file, dob_email_output_file, don_output_file, cp_output_file, metro_output_file = backend.create_file_names()

if slot_files['cp_toronto_west'] is not None and slot_files['cp_hamilton'] is not None:
    cp_package = backend.combine(cp_package_files)
    st.download_button(
        label=f'Download {cp_output_file}',
        data=cp_package,
        file_name=cp_output_file,
        mime="application/pdf",
    )

if slot_files['mx_guelph'] is not None:
    st.download_button(
        label=f'Download {metro_output_file}',
        data=slot_files['mx_guelph'],
        file_name=metro_output_file,
        mime="application/pdf",
    )

if slot_files['mx_don'] is not None:
    don_package = backend.combine(don_package_files)
    st.download_button(
        label=f'Download {don_output_file}',
        data=don_package,
        file_name=don_output_file,
        mime="application/pdf",
    )

if None not in DOB_to_email_files:
    dob_email_package = backend.combine(DOB_to_email_files)
    st.download_button(
        label=f'Download {dob_email_output_file}',
        data=dob_email_package,
        file_name=dob_email_output_file,
        mime="application/pdf",
    )
    dob_print_package = backend.combine(DOB_to_print_files)
    st.download_button(
        label=f'Download {dob_print_output_file}',
        data=dob_print_package,
        file_name=dob_print_output_file,
        mime="application/pdf",
    )
