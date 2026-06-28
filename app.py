import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
st.set_page_config(page_title="Rifa Premium", layout="wide")

DB_FILE = "rifa_db.csv"
PRECIO = 3000
ADMIN_PASSWORD = "1234"
