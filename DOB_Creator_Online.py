import backend
import streamlit as st


st.set_page_config(
    page_title="Alstom-DCOT",
    layout="wide",
)

st.header('Alstom-DCOT')

st.markdown(
    """
    <style>
    div[data-testid="stFileUploader"] section {
        padding: 0.55rem;
        min-height: 4.25rem;
    }
    div[data-testid="stFileUploader"] section p {
        font-size: 0.78rem;
        margin-bottom: 0;
    }
    div[data-testid="stFileUploader"] small {
        display: none;
    }
    .upload-title {
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0.25rem 0 0.2rem;
    }
    .helper-text {
        color: #6b7280;
        font-size: 0.82rem;
        margin: -0.1rem 0 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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



def add_pdf_slot(count_key):
    st.session_state[count_key] += 1


def remove_pdf_slot(count_key, reset_key):
    st.session_state[count_key] = max(1, st.session_state[count_key] - 1)
    st.session_state[reset_key] += 1


def clear_pdf_slots(count_key, reset_key):
    st.session_state[count_key] = 1
    st.session_state[reset_key] += 1


def pdf_uploader(column, title, helper_text, key_prefix, allow_extra=False):
    reset_key = f'{key_prefix}_reset'
    count_key = f'{key_prefix}_pdf_count'
    if reset_key not in st.session_state:
        st.session_state[reset_key] = 0
    if count_key not in st.session_state:
        st.session_state[count_key] = 1

    column.markdown(f'<div class="upload-title">{title}</div>', unsafe_allow_html=True)
    if helper_text:
        column.markdown(f'<div class="helper-text">{helper_text}</div>', unsafe_allow_html=True)

    uploaded_files = []
    for index in range(st.session_state[count_key]):
        uploaded_file = column.file_uploader(
            f'PDF upload {index + 1}',
            type=['pdf'],
            key=f'{key_prefix}_{st.session_state[reset_key]}_{index}',
            label_visibility='collapsed',
        )
        if uploaded_file is not None:
            uploaded_files.append(uploaded_file)

    if allow_extra:
        add_label = 'Add second PDF' if st.session_state[count_key] == 1 else 'Add another PDF'
        column.button(add_label, key=f'add_pdf_{key_prefix}', on_click=add_pdf_slot, args=(count_key,))
        if st.session_state[count_key] > 1:
            column.button(
                'Remove last PDF slot',
                key=f'remove_pdf_slot_{key_prefix}',
                on_click=remove_pdf_slot,
                args=(count_key, reset_key),
            )
        if uploaded_files:
            column.button('Clear PDFs', key=f'clear_{key_prefix}', on_click=clear_pdf_slots, args=(count_key, reset_key))
        return uploaded_files

    if uploaded_files:
        column.button('Remove file', key=f'remove_{key_prefix}', on_click=clear_pdf_slots, args=(count_key, reset_key))
        return uploaded_files[0]
    return None


def render_uploader_grid(upload_slots, columns_per_row=4):
    uploaded_files = {}
    for start in range(0, len(upload_slots), columns_per_row):
        columns = st.columns(columns_per_row)
        for column, slot in zip(columns, upload_slots[start:start + columns_per_row]):
            uploaded_files[slot['key']] = pdf_uploader(
                column,
                slot['title'],
                '',
                slot['key'],
                allow_extra=True,
            )
    return uploaded_files


def get_slot_file(slot, uploaded_files):
    if slot['source'] == 'builtin':
        return slot['path']
    return uploaded_files.get(slot['key'], [])


def flatten_package_files(package_files):
    flat_files = []
    for file in package_files:
        if isinstance(file, list):
            flat_files.extend(file or [None])
        else:
            flat_files.append(file)
    return flat_files


def package_is_ready(package_files):
    return None not in package_files


def package_download_data(package_files):
    if len(package_files) == 1:
        return package_files[0]
    return backend.combine(package_files)


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
st.button('Create Packages')


if dob_cover_page is None:
    dob_cover_page = './PDFs/Permanent DOB  DON Coverpage.pdf'
if don_cover_page is None:
    don_cover_page = './PDFs/Permanent DOB  DON Coverpage.pdf'

slot_files = {
    slot['key']: get_slot_file(slot, uploaded_files)
    for slot in DOB_SLOTS
}

DOB_to_email_files = flatten_package_files([slot_files[slot['key']] for slot in DOB_SLOTS])
DOB_to_print_files = [dob_cover_page] + DOB_to_email_files

don_package_files = flatten_package_files([
    don_cover_page,
    slot_files['mx_don'],
    slot_files['ehs_form'],
    slot_files['radio_channel_guide'],
])
cp_package_files = flatten_package_files([
    slot_files['cp_toronto_west'],
    slot_files['cp_hamilton'],
])
mx_guelph_files = flatten_package_files([slot_files['mx_guelph']])
stratford_package_files = flatten_package_files([
    slot_files['stratford_tgobs'],
    slot_files['goderich_exeter_railway'],
])

# get desktop location and filenames
dob_print_output_file, dob_email_output_file, don_output_file, cp_output_file, metro_output_file = backend.create_file_names()
month, day, year = backend.get_date()
stratford_output_file = f'Stratford DOB {month} {day}, {year}.pdf'

if package_is_ready(cp_package_files):
    cp_package = backend.combine(cp_package_files)
    st.download_button(
        label=f'Download {cp_output_file}',
        data=cp_package,
        file_name=cp_output_file,
        mime="application/pdf",
    )

if package_is_ready(mx_guelph_files):
    st.download_button(
        label=f'Download {metro_output_file}',
        data=package_download_data(mx_guelph_files),
        file_name=metro_output_file,
        mime="application/pdf",
    )

if package_is_ready(stratford_package_files):
    stratford_package = backend.combine(stratford_package_files)
    st.download_button(
        label=f'Download {stratford_output_file}',
        data=stratford_package,
        file_name=stratford_output_file,
        mime="application/pdf",
    )

if package_is_ready(don_package_files):
    don_package = backend.combine(don_package_files)
    st.download_button(
        label=f'Download {don_output_file}',
        data=don_package,
        file_name=don_output_file,
        mime="application/pdf",
    )

if package_is_ready(DOB_to_email_files):
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
