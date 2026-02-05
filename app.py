import streamlit as st
import os
from dotenv import load_dotenv
from utils.llm import ask_llm

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")
    st.title("TalentScout Hiring Assistant")
    st.write("Welcome to the hiring assistant!")

    if "messages" not in st.session_state:
        st.session_state.messages = []


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Action buttons near the bottom
    if st.button("Save Candidate Info", use_container_width=True):
        with st.spinner("Extracting info..."):
            from utils.llm import extract_candidate_info
            from utils.storage import save_candidates, load_candidates
            
            candidate_data = extract_candidate_info(st.session_state.messages)
            if candidate_data:
                if candidate_data.get('full_name') or candidate_data.get('email'):
                    candidates = load_candidates()
                    
                    # Check for duplicates based on email or phone
                    is_duplicate = False
                    new_email = candidate_data.get('email')
                    new_phone = candidate_data.get('phone')
                    
                    for c in candidates:
                        if new_email and c.get('email') == new_email:
                            is_duplicate = True
                            break
                        if new_phone and c.get('phone') == new_phone:
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        st.warning("Candidate already exists!")
                    else:
                        candidates.append(candidate_data)
                        save_candidates(candidates)
                        st.success("Candidate saved!")
                else:
                    st.warning("Could not extract enough information yet.")
            else:
                st.error("Failed to extract information.")

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in ask_llm(st.session_state.messages):
                full_response += response
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
