import streamlit as st
import pandas as pd
import re
import pytesseract
from PIL import Image

# Configuração da página
st.set_page_config(page_title="Scanner AçoNobre", page_icon="📱", layout="centered")

st.title("📱 Leitor de Produção - AçoNobre")
st.write("Tire uma foto da etiqueta para extrair o Código da Peça.")

foto = st.file_uploader("📸 Clique para Tirar Foto", type=["png", "jpg", "jpeg"])

if foto is not None:
    with st.spinner("A analisar a etiqueta..."):
        try:
            # Abre a imagem
            img = Image.open(foto)
            texto_lido = pytesseract.image_to_string(img)
            
            # 1. CAÇA AO CÓDIGO FILHO (Ex: 901.002191 - Tem sempre o ponto!)
            match_filho = re.search(r'(\d{3}\.\d{6})', texto_lido)
            codigo_filho = match_filho.group(1) if match_filho else None
            
            # 2. CAÇA AO CÓDIGO PAI (Ex: 8092177 - O SigmaNest tira o ponto)
            match_pai = re.search(r'(\d{7})', texto_lido)
            codigo_pai_bruto = match_pai.group(1) if match_pai else None
            
            # 3. CAÇA AO PEDIDO
            match_pd = re.search(r'PD[\s:-]*(\d+)', texto_lido, re.IGNORECASE)
            pedido = match_pd.group(1) if match_pd else None
            
            # EXIBIÇÃO NO ECRÃ
            if codigo_filho:
                st.success("✅ Código da Peça encontrado!")
                
                # Destaque máximo para o Código Filho
                st.markdown(f"""
                <div style="background-color: #1e3d59; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                    <h3 style="color: white; margin: 0;">CÓDIGO DA PEÇA (FILHO)</h3>
                    <h1 style="color: #ffc13b; margin: 0; font-size: 40px;">{codigo_filho}</h1>
                </div>
                """, unsafe_allow_html=True)
                
                # Exibe o Pai formatado se encontrar
                if codigo_pai_bruto:
                    pai_formatado = f"{codigo_pai_bruto[:3]}.00{codigo_pai_bruto[3:]}"
                    st.info(f"🏗️ **Pertence ao Pai:** {pai_formatado}")
                else:
                    st.warning("⚠️ **Pai:** Não identificado na foto.")
                
                # Exibe o Pedido se encontrar
                if pedido:
                    st.info(f"📦 **Pedido associado:** {pedido}")
                else:
                    st.warning("⚠️ **Pedido:** Não identificado na foto.")
                
            else:
                st.error("❌ Não foi possível encontrar o Código da Peça (formato XXX.XXXXXX). Tente focar melhor.")
                
            with st.expander("Ver texto bruto lido pela câmara"):
                st.write(texto_lido)
                    
        except Exception as e:
            st.error(f"Erro ao processar a imagem: {e}")