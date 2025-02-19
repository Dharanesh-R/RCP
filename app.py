import streamlit as st
import requests
import tempfile
import os

# Backend URL (Flask API)

BACKEND_URL = "http://127.0.0.1:5000"

# Set custom page configuration
st.set_page_config(
    page_title="AI Sprint Planner",
    page_icon="📜",
    layout="centered"
)

# Apply fantasy theme styles
st.markdown(
    """
    <style>
        /* Import fantasy-style fonts */
        @import url('https://fonts.googleapis.com/css2?family=MedievalSharp&family=IM+Fell+English+SC&display=swap');

        /* Background image */
        body {
            background: url('https://images.unsplash.com/photo-1518917177812-8367d88291ec') no-repeat center center fixed;
            background-size: cover;
            color: #f8f8f2;
        }

        /* Container styling */
        .block-container {
            background: rgba(20, 20, 20, 0.85);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0px 0px 15px rgba(255, 255, 255, 0.3);
            max-width: 700px;
            margin-top: 100px;
        }

        /* Title */
        h1 {
            font-family: 'IM Fell English SC', serif;
            font-size: 38px;
            color: #f4e4ba;
            text-shadow: 3px 3px 10px #f8c291;
            text-align: center;
        }

        /* File uploader styling */
        .stFileUploader {
            border: 2px dashed #f4e4ba !important;
            border-radius: 10px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
        }

       /* Buttons */
        div.stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #ff007f, #ff5733);
            color: white;
            font-size: 18px;
            padding: 12px;
            border-radius: 10px;
            border: none;
            font-family: 'Comic Sans MS', cursive;
            box-shadow: 0px 0px 15px #ff007f;
            transition: 0.3s ease-in-out;
        }
        
        div.stButton > button:hover {
            background: linear-gradient(135deg, #ff5733, #ff007f);
            box-shadow: 0px 0px 25px #ff007f;
            transform: scale(1.05);
            color: white;
        }

        .stAlert {
            border-radius: 8px;
            padding: 15px;
            font-family: 'Comic Sans MS', cursive;
        }

        /* Centered download button */
        .download-container {
            text-align: center;
            margin-top: 20px;
        }

        .download-button {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #218838);
            color: white;
            font-size: 18px;
            padding: 12px 20px;
            border-radius: 10px;
            border: none;
            font-family: 'Comic Sans MS', cursive;
            box-shadow: 0px 0px 15px #28a745;
            transition: 0.3s ease-in-out;
            text-decoration: none;
        }

        .download-button:hover {
            background: linear-gradient(135deg, #218838, #28a745);
            box-shadow: 0px 0px 25px #28a745;
            transform: scale(1.05);
            color: white;
        }

    </style>
    """,
    unsafe_allow_html=True
)

# App Title
st.markdown("<h1>The Enchanted Sprint Planner</h1>", unsafe_allow_html=True)
st.write("Upload an **Word Document `.docx`** containing user stories, and our AI will transform it into a **magical Sprint Plan**! ")

# File Uploader
uploaded_file = st.file_uploader(
    "Summon Your Document",
    type=["docx"]
)

if uploaded_file:
    if st.button("Submit"):
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name

            # Send file to backend
            with open(temp_file_path, "rb") as file:
                files = {"file": file}
                response = requests.post(f"{BACKEND_URL}/download_sprint_plan", files=files)

            os.remove(temp_file_path)  # Cleanup temp file

            if response.status_code == 200:
                pdf_filename = "sprint_plan.pdf"

                # Save PDF temporarily
                with open(pdf_filename, "wb") as f:
                    f.write(response.content)

                # Provide direct download
                st.markdown('<div class="download-container">', unsafe_allow_html=True)
                with open(pdf_filename, "rb") as f:
                    st.download_button(
                        label="📜 Download Sprint Plan",
                        data=f,
                        file_name="sprint_plan.pdf",
                        mime="application/pdf",
                        key="download_button"
                    )
                st.markdown("</div>", unsafe_allow_html=True)

                os.remove(pdf_filename)  # Cleanup after download
            else:
                st.error("Download failed! Try again.")

        except Exception as e:
            st.error(f"Error occurred: {e}")
