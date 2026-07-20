import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Scanner AçoNobre", page_icon="📱", layout="centered")

st.title("📱 Leitor de Produção - AçoNobre")
st.write("Aponte a câmara para a etiqueta do SigmaNest.")

# Ativa a câmara do telemóvel
foto = st.camera_input("Tirar foto da etiqueta")

if foto is not None:
    with st.spinner("A analisar a etiqueta..."):
        try:
            # Abre a imagem
            img = Image.open(foto)
            
            # Lê o texto da imagem usando o Tesseract
            texto_lido = pytesseract.image_to_string(img)
            
            # Aplica a nossa lógica de extração
            match_pd = re.search(r'PD:\s*(\d+)', texto_lido)
            pedido = match_pd.group(1) if match_pd else None
            
            match_codigo = re.search(r'-\s*(\d{7})', texto_lido)
            codigo_sigma = match_codigo.group(1) if match_codigo else None
            
            if pedido and codigo_sigma:
                # O Pulo do Gato: Corrige a formatação
                codigo_formatado = f"{codigo_sigma[:3]}.00{codigo_sigma[3:]}"
                
                st.success("✅ Etiqueta Lida com Sucesso!")
                
                # Exibe os dados de forma bonita num cartão
                st.info(f"📦 **PEDIDO:** {pedido}")
                st.info(f"⚙️ **CÓDIGO (Delta/PCP):** {codigo_formatado}")
                
                # Espaço reservado para o cruzamento com o Excel
                st.markdown("---")
                st.write("*(Aqui entrará a ligação com a base de dados do PCP para mostrar o **Item Pai** e a **Descrição**)*")
                
            else:
                st.error("❌ Não foi possível extrair os dados. Tente focar melhor a câmara ou melhorar a iluminação.")
                with st.expander("Ver texto bruto lido pela câmara"):
                    st.write(texto_lido)
                    
        except Exception as e:
            st.error(f"Erro ao processar a imagem: {e}")