from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import backend
import streamlit as st


st.set_page_config(
    page_title="Alstom-DCOT",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_COVER_PAGE = "./PDFs/Permanent DOB  DON Coverpage.pdf"
STATIC_DOB_DOCUMENTS = [
    ("Predeparture Checklist", "./PDFs/Predeparture Checklist Template  - 2025-12-22.pdf"),
    ("EHS Concern Form", "./PDFs/EHS Concern  Form updated PDF 10.04.2026.pdf"),
    ("Reversing Re-Spotting Checklist", "./PDFs/Reversing Re-Spotting Checklist updated April 02 2026.pdf"),
    ("CROR 115 Grade Crossings", "./PDFs/Re-spotting an Overshoot and the Application of CROR 115 at Grade Crossings.pdf"),
    ("En Route Job Briefings", "./PDFs/En route job briefings - Rev Apr 16, 2026.pdf"),
    ("Station to Station Notepad", "./PDFs/Station to Station Notepad.pdf"),
    ("DMU Transponder Loops", "./PDFs/12.15. DMU Transponder Loops - Job Aid.pdf"),
    ("CPKC Signal Authority", "./PDFs/CPKC Signal Authority Form (Apr10).pdf"),
    ("Radio Channel Guide", "./PDFs/Radio Channel Guide July 23rd.pdf"),
]

UPLOAD_FIELDS = [
    {"key": "gta", "title": "Greater Metro", "help": "Required for the full DOB package."},
    {"key": "bala", "title": "Metrolinx Bala", "help": "Required for the full DOB package."},
    {"key": "don", "title": "Metrolinx DON", "help": "Creates the DON package and is required for full DOB."},
    {"key": "cp_west", "title": "CPKC West", "help": "Upload with CPKC Hamilton to create the CP package."},
    {"key": "cp_hamilton", "title": "CPKC Hamilton", "help": "Upload with CPKC West to create the CP package."},
    {"key": "metrolinx_guelph", "title": "Metrolinx Guelph", "help": "Creates a separate Metrolinx package and is required for full DOB."},
    {"key": "goderich_exeter", "title": "DOB Goderich & Exeter Railway", "help": "Required for the full DOB package."},
]

PACKAGE_ORDER = ["dob_email", "dob_print", "don", "cp", "metro"]


@st.cache_data(show_spinner=False)
def build_pdf_package(sources):
    """Cache package assembly so widget changes do not re-merge unchanged PDFs."""
    return backend.combine(sources).getvalue()


def as_upload_source(uploaded_file):
    if uploaded_file is None:
        return None
    return ("upload", uploaded_file.name, uploaded_file.getvalue())


def as_path_source(label, path):
    return ("path", label, path)


def source_name(source):
    return source[1] if source is not None else "Missing"


def make_zip(packages):
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as archive:
        for package_key in PACKAGE_ORDER:
            package = packages.get(package_key)
            if package:
                archive.writestr(package["file_name"], package["data"])
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def upload_card(field):
    return st.file_uploader(
        field["title"],
        type=["pdf"],
        key=f"upload_{field['key']}",
        help=field["help"],
    )


def status_pill(is_ready, ready_text, missing_text):
    if is_ready:
        st.success(ready_text, icon="✅")
    else:
        st.warning(missing_text, icon="⚠️")


if "packages" not in st.session_state:
    st.session_state.packages = {}
if "last_summary" not in st.session_state:
    st.session_state.last_summary = []

with st.sidebar:
    st.title("Alstom-DCOT")
    st.caption("Compact package generator")
    include_zip = st.checkbox("Create one ZIP with all generated packages", value=True)
    include_validation_log = st.checkbox("Include validation summary on screen", value=True)
    st.divider()
    if st.button("Reset generated packages", use_container_width=True):
        st.session_state.packages = {}
        st.session_state.last_summary = []
        st.rerun()
    st.caption("Tip: use the small X on each uploaded file to remove or replace it.")

st.title("🚆 Alstom-DCOT Package Generator")
st.caption("Upload the variable PDFs once, review readiness, then generate only the packages that are complete.")

setup_tab, output_tab, help_tab = st.tabs(["1. Upload & Generate", "2. Downloads", "Help"])

with setup_tab:
    with st.form("package_form"):
        cover_col, status_col = st.columns([1.1, 1])

        with cover_col:
            with st.expander("Cover pages", expanded=False):
                dob_cover_page_upload = st.file_uploader(
                    "DOB Cover Page",
                    type=["pdf"],
                    key="upload_dob_cover_page",
                    help="Leave blank to use the default cover page.",
                )
                don_cover_page_upload = st.file_uploader(
                    "DON Cover Page",
                    type=["pdf"],
                    key="upload_don_cover_page",
                    help="Leave blank to use the default cover page.",
                )
                st.caption("Blank cover uploads automatically use the permanent default cover page.")

        with status_col:
            st.subheader("Workflow")
            st.markdown(
                """
                1. Upload route PDFs  
                2. Review package readiness  
                3. Generate complete packages  
                4. Download individual PDFs or one ZIP
                """
            )

        st.subheader("Route PDFs")
        upload_cols = st.columns(3)
        uploads = {}
        for index, field in enumerate(UPLOAD_FIELDS):
            with upload_cols[index % 3]:
                uploads[field["key"]] = upload_card(field)

        submitted = st.form_submit_button("Generate DCOT Packages", type="primary", use_container_width=True)

    sources = {key: as_upload_source(file) for key, file in uploads.items()}
    dob_cover_page = as_upload_source(dob_cover_page_upload) or as_path_source("Default DOB Cover Page", DEFAULT_COVER_PAGE)
    don_cover_page = as_upload_source(don_cover_page_upload) or as_path_source("Default DON Cover Page", DEFAULT_COVER_PAGE)

    dob_email_sources = (
        sources["gta"],
        sources["bala"],
        as_path_source(*STATIC_DOB_DOCUMENTS[0]),
        as_path_source(*STATIC_DOB_DOCUMENTS[1]),
        as_path_source(*STATIC_DOB_DOCUMENTS[2]),
        as_path_source(*STATIC_DOB_DOCUMENTS[3]),
        as_path_source(*STATIC_DOB_DOCUMENTS[4]),
        as_path_source(*STATIC_DOB_DOCUMENTS[5]),
        as_path_source(*STATIC_DOB_DOCUMENTS[6]),
        sources["don"],
        sources["cp_west"],
        sources["cp_hamilton"],
        as_path_source(*STATIC_DOB_DOCUMENTS[7]),
        sources["metrolinx_guelph"],
        sources["goderich_exeter"],
        as_path_source(*STATIC_DOB_DOCUMENTS[8]),
    )
    dob_print_sources = (dob_cover_page,) + dob_email_sources
    don_sources = (don_cover_page, sources["don"], as_path_source(*STATIC_DOB_DOCUMENTS[1]), as_path_source(*STATIC_DOB_DOCUMENTS[8]))
    cp_sources = (sources["cp_west"], sources["cp_hamilton"])
    metro_sources = (sources["metrolinx_guelph"],)

    required_for_dob = [field["key"] for field in UPLOAD_FIELDS]
    missing_dob = [field["title"] for field in UPLOAD_FIELDS if sources[field["key"]] is None]
    missing_cp = ["CPKC West" if sources["cp_west"] is None else None, "CPKC Hamilton" if sources["cp_hamilton"] is None else None]
    missing_cp = [item for item in missing_cp if item]

    st.subheader("Readiness Summary")
    summary_cols = st.columns(4)
    with summary_cols[0]:
        status_pill(not missing_dob, "Full DOB ready", f"DOB missing {len(missing_dob)} upload(s)")
    with summary_cols[1]:
        status_pill(sources["don"] is not None, "DON ready", "DON package needs Metrolinx DON")
    with summary_cols[2]:
        status_pill(not missing_cp, "CPKC ready", f"CPKC missing {len(missing_cp)} upload(s)")
    with summary_cols[3]:
        status_pill(sources["metrolinx_guelph"] is not None, "Metrolinx ready", "Metrolinx package needs Guelph")

    if include_validation_log:
        with st.expander("Validation details", expanded=bool(missing_dob)):
            st.write(f"Uploaded route PDFs: **{sum(source is not None for source in sources.values())} / {len(UPLOAD_FIELDS)}**")
            if missing_dob:
                st.write("Missing for full DOB package:")
                for item in missing_dob:
                    st.write(f"- {item}")
            else:
                st.write("All route PDFs required for the full DOB package are present.")
            st.write("Package source order is preserved for the DOB print/email outputs.")

    if submitted:
        package_names = backend.create_file_names()
        dob_print_output_file, dob_email_output_file, don_output_file, cp_output_file, metro_output_file = package_names
        packages = {}
        generated_summary = []

        with st.status("Generating complete packages...", expanded=True) as status:
            if all(source is not None for source in dob_email_sources):
                packages["dob_email"] = {
                    "label": "Complete DOB Package",
                    "file_name": dob_email_output_file,
                    "data": build_pdf_package(dob_email_sources),
                }
                packages["dob_print"] = {
                    "label": "Complete DOB Package - print version",
                    "file_name": dob_print_output_file,
                    "data": build_pdf_package(dob_print_sources),
                }
                generated_summary.append("Full DOB email and print packages generated.")
                st.write("✅ Full DOB email and print packages")
            else:
                st.write("⚠️ Full DOB skipped because required uploads are missing.")

            if sources["don"] is not None:
                packages["don"] = {
                    "label": "DON Package",
                    "file_name": don_output_file,
                    "data": build_pdf_package(don_sources),
                }
                generated_summary.append("DON package generated.")
                st.write("✅ DON package")
            else:
                st.write("⚠️ DON skipped because Metrolinx DON is missing.")

            if all(source is not None for source in cp_sources):
                packages["cp"] = {
                    "label": "CPKC DOB Package",
                    "file_name": cp_output_file,
                    "data": build_pdf_package(cp_sources),
                }
                generated_summary.append("CPKC package generated.")
                st.write("✅ CPKC package")
            else:
                st.write("⚠️ CPKC skipped because West and/or Hamilton is missing.")

            if sources["metrolinx_guelph"] is not None:
                packages["metro"] = {
                    "label": "Metrolinx DOB Package",
                    "file_name": metro_output_file,
                    "data": build_pdf_package(metro_sources),
                }
                generated_summary.append("Metrolinx package generated.")
                st.write("✅ Metrolinx package")
            else:
                st.write("⚠️ Metrolinx skipped because Guelph is missing.")

            status.update(label="Package generation complete", state="complete")

        st.session_state.packages = packages
        st.session_state.last_summary = generated_summary
        if packages:
            st.success("Packages are ready in the Downloads tab.", icon="✅")
        else:
            st.error("No packages were generated. Upload at least one complete package set.", icon="❌")

with output_tab:
    st.subheader("Downloads")
    packages = st.session_state.packages

    if not packages:
        st.info("Generate packages from the Upload & Generate tab first.")
    else:
        if st.session_state.last_summary:
            st.write("Generation summary:")
            for item in st.session_state.last_summary:
                st.write(f"- {item}")

        if include_zip and len(packages) > 1:
            st.download_button(
                "Download All Generated Packages (.zip)",
                data=make_zip(packages),
                file_name="Alstom-DCOT Packages.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
            )
            st.divider()

        download_cols = st.columns(2)
        visible_index = 0
        for package_key in PACKAGE_ORDER:
            package = packages.get(package_key)
            if not package:
                continue
            with download_cols[visible_index % 2]:
                st.download_button(
                    f"Download {package['file_name']}",
                    data=package["data"],
                    file_name=package["file_name"],
                    mime="application/pdf",
                    use_container_width=True,
                )
            visible_index += 1

with help_tab:
    st.subheader("What changed in this preview")
    st.markdown(
        """
        - Cleaner three-column upload area to reduce vertical scrolling.
        - Cover pages moved into an optional expander.
        - Readiness cards show which packages can be generated before processing.
        - Packages generate only after pressing the primary button.
        - PDF merging is cached for unchanged inputs.
        - Downloads are grouped in one tab, with an optional all-in-one ZIP.
        - Detailed validation is hidden unless needed.
        """
    )
    st.subheader("Required uploads for full DOB")
    for key in required_for_dob:
        label = next(field["title"] for field in UPLOAD_FIELDS if field["key"] == key)
        st.write(f"- {label}")
