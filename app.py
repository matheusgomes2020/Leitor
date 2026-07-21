import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Scanner AçoNobre", page_icon="📱", layout="centered")

st.title("📱 Leitor de Produção - AçoNobre")
st.write("Tire uma foto da etiqueta para leitura.")

foto = st.file_uploader("📸 Clique para Tirar Foto", type=["png", "jpg", "jpeg"])

if foto is not None:
    with st.spinner("A analisar a etiqueta..."):
        try:
            # Abre a imagem
            img = Image.open(foto)
            
            # Lê o texto da imagem usando o Tesseract
            texto_lido = pytesseract.image_to_string(img)
            
            # 1. CAÇA AO PEDIDO (Aceita PD:, PD-, PD_ ou só PD seguido de números)
            match_pd = re.search(r'PD[\s:-]*(\d+)', texto_lido, re.IGNORECASE)
            pedido = match_pd.group(1) if match_pd else None
            
            # 2. CAÇA AO CÓDIGO (Modo Trator: procura apenas 7 números seguidos, ignora o traço)
            match_codigo = re.search(r'(\d{7})', texto_lido)
            codigo_sigma = match_codigo.group(1) if match_codigo else None
            
            if pedido and codigo_sigma:
                # Corrige a formatação
                codigo_formatado = f"{codigo_sigma[:3]}.00{codigo_sigma[3:]}"
                
                st.success("✅ Etiqueta Lida com Sucesso!")
                
                # Exibe os dados
                st.info(f"📦 **PEDIDO:** {pedido}")
                st.info(f"⚙️ **CÓDIGO (Delta/PCP):** {codigo_formatado}")
                
                st.markdown("---")
                st.write("*(Pronto para conectar com o Excel do PCP!)*")
                
            else:
                st.error("❌ Faltam dados. A câmara não conseguiu ler o Pedido ou os 7 dígitos do Código.")
                with st.expander("Ver texto bruto lido pela câmara"):
                    st.write(texto_lido)
                    
        except Exception as e:
            st.error(f"Erro ao processar a imagem: {e}")